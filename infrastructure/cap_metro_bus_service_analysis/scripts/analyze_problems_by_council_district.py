from __future__ import annotations

from pathlib import Path
import re

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_TABLES = ROOT / "output" / "tables"
OUTPUT_REPORTS = ROOT / "reports"


def normalize_stop_name(value: object) -> str:
    text = str(value).strip().lower()
    text = text.replace(" station", "")
    text = re.sub(r"\(.*?\)", "", text)
    text = text.replace("&", "/")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_column(df: pd.DataFrame, candidates: list[str]) -> str:
    lowered = {c.lower().strip(): c for c in df.columns}
    for candidate in candidates:
        key = candidate.lower().strip()
        if key in lowered:
            return lowered[key]

    for col in df.columns:
        col_key = col.lower().strip()
        for candidate in candidates:
            if candidate.lower().strip() in col_key:
                return col

    raise KeyError(f"Could not find any candidate column: {candidates}")


def min_max_scale(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    low = values.min()
    high = values.max()
    if high == low:
        return pd.Series(np.zeros(len(values)), index=values.index)
    return (values - low) / (high - low)


def is_unresolved(status_value: object) -> bool:
    status = str(status_value).strip().lower()
    if not status or status == "nan":
        return False

    unresolved_markers = ["open", "pending", "assigned", "in progress", "reopen", "on hold", "new"]
    resolved_markers = ["closed", "resolved", "complete", "completed"]

    if any(marker in status for marker in resolved_markers):
        return False
    return any(marker in status for marker in unresolved_markers)


def build_stop_level_problem_table() -> pd.DataFrame:
    geo = pd.read_csv(OUTPUT_TABLES / "stop_geospatial_equity.csv")
    baseline = pd.read_csv(OUTPUT_TABLES / "stop_baseline_risk_index.csv")
    detailed = pd.read_csv(ROOT / "data" / "canonical" / "311_detailed_complaint_report.csv")

    geo_stop_id_col = find_column(geo, ["stop_id"])
    geo_stop_name_col = find_column(geo, ["stop_name"])
    district_col = find_column(geo, ["council_district", "district"])

    baseline_stop_id_col = find_column(baseline, ["stop_id"])
    baseline_stop_name_col = find_column(baseline, ["stop_name"])

    status_col = find_column(detailed, ["Status", "SR Status"])
    detailed_stop_col = find_column(detailed, ["Stop Name", "stop_name"])

    detailed = detailed.copy()
    detailed["normalized_stop"] = detailed[detailed_stop_col].map(normalize_stop_name)
    detailed["unresolved_tickets"] = detailed[status_col].map(is_unresolved).astype(int)

    unresolved_by_stop = (
        detailed.groupby("normalized_stop", as_index=False)
        .agg(
            total_311_calls_detail=(status_col, "count"),
            unresolved_tickets=("unresolved_tickets", "sum"),
        )
        .copy()
    )
    unresolved_by_stop["unresolved_rate"] = np.where(
        unresolved_by_stop["total_311_calls_detail"] > 0,
        unresolved_by_stop["unresolved_tickets"] / unresolved_by_stop["total_311_calls_detail"],
        0,
    )

    geo_small = geo[[geo_stop_id_col, geo_stop_name_col, district_col, "amenity_gap", "total_calls"]].copy()
    geo_small.columns = ["stop_id", "stop_name_geo", "council_district", "amenity_gap", "total_calls"]
    geo_small["normalized_stop"] = geo_small["stop_name_geo"].map(normalize_stop_name)

    baseline_small = baseline[[baseline_stop_id_col, baseline_stop_name_col, "risk_score", "safety_concerns"]].copy()
    baseline_small.columns = ["stop_id", "stop_name", "risk_score", "safety_concerns"]
    baseline_small["normalized_stop"] = baseline_small["stop_name"].map(normalize_stop_name)

    merged = geo_small.merge(
        baseline_small[["stop_id", "risk_score", "safety_concerns", "stop_name"]],
        on="stop_id",
        how="left",
    )

    merged["stop_name"] = merged["stop_name"].fillna(merged["stop_name_geo"])

    merged = merged.merge(
        unresolved_by_stop[["normalized_stop", "total_311_calls_detail", "unresolved_tickets", "unresolved_rate"]],
        on="normalized_stop",
        how="left",
    )

    merged["council_district"] = merged["council_district"].astype(str).str.strip()
    merged["total_calls"] = pd.to_numeric(merged["total_calls"], errors="coerce").fillna(0)
    merged["amenity_gap"] = pd.to_numeric(merged["amenity_gap"], errors="coerce").fillna(0)
    merged["risk_score"] = pd.to_numeric(merged["risk_score"], errors="coerce").fillna(0)
    merged["safety_concerns"] = pd.to_numeric(merged["safety_concerns"], errors="coerce").fillna(0)
    merged["unresolved_tickets"] = pd.to_numeric(merged["unresolved_tickets"], errors="coerce").fillna(0)
    merged["unresolved_rate"] = pd.to_numeric(merged["unresolved_rate"], errors="coerce").fillna(0)

    merged["problem_score"] = (
        min_max_scale(merged["risk_score"]) * 0.40
        + min_max_scale(merged["total_calls"]) * 0.20
        + min_max_scale(merged["unresolved_tickets"]) * 0.20
        + min_max_scale(merged["safety_concerns"]) * 0.10
        + min_max_scale(merged["amenity_gap"]) * 0.10
    )

    merged = merged.sort_values(["council_district", "problem_score"], ascending=[True, False]).copy()
    merged["rank_in_district"] = (
        merged.groupby("council_district")["problem_score"].rank(method="first", ascending=False).astype(int)
    )

    out_cols = [
        "council_district",
        "rank_in_district",
        "stop_id",
        "stop_name",
        "problem_score",
        "risk_score",
        "total_calls",
        "unresolved_tickets",
        "unresolved_rate",
        "safety_concerns",
        "amenity_gap",
    ]

    out_df = merged[out_cols].copy()
    out_df["problem_score"] = out_df["problem_score"].round(3)
    out_df["risk_score"] = out_df["risk_score"].round(3)
    out_df["unresolved_rate"] = (out_df["unresolved_rate"] * 100).round(1)

    return out_df


def build_district_summary(stop_rank: pd.DataFrame) -> pd.DataFrame:
    summary = (
        stop_rank.groupby("council_district", as_index=False)
        .agg(
            stops_analyzed=("stop_id", "count"),
            avg_problem_score=("problem_score", "mean"),
            max_problem_score=("problem_score", "max"),
            total_calls=("total_calls", "sum"),
            unresolved_tickets=("unresolved_tickets", "sum"),
            avg_unresolved_rate_pct=("unresolved_rate", "mean"),
        )
        .copy()
    )

    top_stop_per_district = (
        stop_rank.sort_values(["council_district", "problem_score"], ascending=[True, False])
        .groupby("council_district", as_index=False)
        .first()[["council_district", "stop_name"]]
        .rename(columns={"stop_name": "top_problem_stop"})
    )

    summary = summary.merge(top_stop_per_district, on="council_district", how="left")
    summary = summary.sort_values(["avg_problem_score", "total_calls"], ascending=[False, False]).copy()

    summary["avg_problem_score"] = summary["avg_problem_score"].round(3)
    summary["max_problem_score"] = summary["max_problem_score"].round(3)
    summary["avg_unresolved_rate_pct"] = summary["avg_unresolved_rate_pct"].round(1)

    return summary


def write_report(stop_rank: pd.DataFrame, district_summary: pd.DataFrame) -> None:
    top_district = district_summary.iloc[0]
    top_stops = stop_rank.sort_values("problem_score", ascending=False).head(10)

    lines = [
        "<!-- markdownlint-disable -->",
        "",
        "# Council District Stop Problem Analysis",
        "",
        "This analysis ranks stops by problem concentration and summarizes burden by council district.",
        "",
        "## Method",
        "",
        "Problem score weights:",
        "- 40% baseline risk score",
        "- 20% total 311 calls",
        "- 20% unresolved 311 tickets",
        "- 10% safety concerns",
        "- 10% amenity gap",
        "",
        "All components are min-max scaled before weighting.",
        "",
        "## Highest-Burden District In This Run",
        "",
        f"- Council District: {top_district['council_district']}",
        f"- Avg problem score: {top_district['avg_problem_score']}",
        f"- Total calls: {int(top_district['total_calls'])}",
        f"- Total unresolved tickets: {int(top_district['unresolved_tickets'])}",
        f"- Top problem stop: {top_district['top_problem_stop']}",
        "",
        "## Top 10 Stops By Problem Score",
        "",
    ]

    for _, row in top_stops.iterrows():
        lines.append(
            f"- District {row['council_district']}: {row['stop_name']} "
            f"(score {row['problem_score']}, calls {int(row['total_calls'])}, "
            f"unresolved {int(row['unresolved_tickets'])}, unresolved rate {row['unresolved_rate']}%)"
        )

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- output/tables/stops_problem_rank_by_council_district.csv",
            "- output/tables/council_district_problem_summary.csv",
            "- output/figures/district_top_problem_stops_bar.png",
            "- output/figures/district_unresolved_totals_bar.png",
        ]
    )

    OUTPUT_REPORTS.mkdir(parents=True, exist_ok=True)
    (OUTPUT_REPORTS / "Council_District_Problem_Analysis.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

    stop_rank = build_stop_level_problem_table()
    district_summary = build_district_summary(stop_rank)

    stop_rank.to_csv(OUTPUT_TABLES / "stops_problem_rank_by_council_district.csv", index=False)
    district_summary.to_csv(OUTPUT_TABLES / "council_district_problem_summary.csv", index=False)
    write_report(stop_rank, district_summary)

    top_district = district_summary.iloc[0]
    print("Council district problem analysis completed.")
    print(f"Top district by average problem score: {top_district['council_district']}")
    print(f"Top stop in that district: {top_district['top_problem_stop']}")


if __name__ == "__main__":
    main()
