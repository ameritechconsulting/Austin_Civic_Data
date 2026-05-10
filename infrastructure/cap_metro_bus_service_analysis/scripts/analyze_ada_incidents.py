from __future__ import annotations

from pathlib import Path
import re

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = ROOT / "data" / "canonical" / "ada_violation_dataset.csv"
OUTPUT_TABLES = ROOT / "output" / "tables"
OUTPUT_REPORTS = ROOT / "reports"


def normalize_stop_name(value: object) -> str:
    text = str(value).strip()
    if not text:
        return "Unknown"
    return re.sub(r"\s+", " ", text)


def find_col(df: pd.DataFrame, candidates: list[str]) -> str:
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

    raise KeyError(f"Missing required column from candidates: {candidates}")


def is_unresolved(status_value: object) -> bool:
    status = str(status_value).strip().lower()
    if not status or status == "nan":
        return False

    resolved_markers = ["closed", "resolved", "complete", "completed"]
    unresolved_markers = ["open", "pending", "assigned", "in progress", "reopen", "on hold", "new"]

    if any(marker in status for marker in resolved_markers):
        return False
    return any(marker in status for marker in unresolved_markers)


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    stop_col = find_col(df, ["Stop Name", "Normalized Stop Name"])
    category_col = find_col(df, ["Category"])
    year_col = find_col(df, ["Year", "Created Date"])
    status_col = find_col(df, ["Status", "SR Status"])
    age_col = find_col(df, ["Age Days"])
    party_col = find_col(df, ["Responsible Party"])

    out = df.copy()

    if "year" in year_col.lower():
        out["year"] = pd.to_numeric(out[year_col], errors="coerce")
    else:
        out["year"] = pd.to_datetime(out[year_col], errors="coerce").dt.year

    out["stop_name"] = out[stop_col].map(normalize_stop_name)
    out["category"] = out[category_col].astype(str).str.strip()
    out["responsible_party"] = out[party_col].astype(str).str.strip()
    out["age_days"] = pd.to_numeric(out[age_col], errors="coerce")
    out["is_unresolved"] = out[status_col].map(is_unresolved)

    by_year = (
        out.groupby("year", as_index=False)
        .agg(
            ada_incidents=("category", "count"),
            unresolved_incidents=("is_unresolved", "sum"),
            avg_age_days=("age_days", "mean"),
        )
        .sort_values("year")
    )
    by_year["unresolved_rate_pct"] = (
        by_year["unresolved_incidents"] / by_year["ada_incidents"] * 100
    ).round(1)
    by_year["avg_age_days"] = by_year["avg_age_days"].round(1)

    by_category = (
        out.groupby("category", as_index=False)
        .agg(
            ada_incidents=("category", "count"),
            unresolved_incidents=("is_unresolved", "sum"),
        )
        .sort_values("ada_incidents", ascending=False)
    )
    by_category["unresolved_rate_pct"] = (
        by_category["unresolved_incidents"] / by_category["ada_incidents"] * 100
    ).round(1)

    by_stop = (
        out.groupby("stop_name", as_index=False)
        .agg(
            ada_incidents=("category", "count"),
            unresolved_incidents=("is_unresolved", "sum"),
            avg_age_days=("age_days", "mean"),
        )
        .sort_values(["ada_incidents", "unresolved_incidents"], ascending=[False, False])
    )
    by_stop["avg_age_days"] = by_stop["avg_age_days"].round(1)
    by_stop["unresolved_rate_pct"] = (
        by_stop["unresolved_incidents"] / by_stop["ada_incidents"] * 100
    ).round(1)

    by_party = (
        out.groupby("responsible_party", as_index=False)
        .agg(
            ada_incidents=("category", "count"),
            unresolved_incidents=("is_unresolved", "sum"),
        )
        .sort_values("ada_incidents", ascending=False)
    )
    by_party["unresolved_rate_pct"] = (
        by_party["unresolved_incidents"] / by_party["ada_incidents"] * 100
    ).round(1)

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORTS.mkdir(parents=True, exist_ok=True)

    by_year.to_csv(OUTPUT_TABLES / "ada_incidents_by_year.csv", index=False)
    by_category.to_csv(OUTPUT_TABLES / "ada_incidents_by_category.csv", index=False)
    by_stop.to_csv(OUTPUT_TABLES / "ada_incidents_by_stop.csv", index=False)
    by_stop.head(15).to_csv(OUTPUT_TABLES / "ada_top15_stops.csv", index=False)
    by_party.to_csv(OUTPUT_TABLES / "ada_incidents_by_responsible_party.csv", index=False)

    total = int(len(out))
    unresolved = int(out["is_unresolved"].sum())
    unresolved_rate = round(unresolved / total * 100, 1) if total > 0 else 0.0

    top_stop = by_stop.iloc[0] if not by_stop.empty else None

    lines = [
        "<!-- markdownlint-disable -->",
        "",
        "# ADA Incident Analysis",
        "",
        "## Headline",
        "",
        f"- Total ADA-related incidents in current dataset: {total}",
        f"- Unresolved incidents: {unresolved} ({unresolved_rate}%)",
    ]

    if top_stop is not None:
        lines.extend(
            [
                f"- Highest-volume stop: {top_stop['stop_name']} ({int(top_stop['ada_incidents'])} incidents)",
                f"- Highest-volume stop unresolved: {int(top_stop['unresolved_incidents'])} ({top_stop['unresolved_rate_pct']}%)",
            ]
        )

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- output/tables/ada_incidents_by_year.csv",
            "- output/tables/ada_incidents_by_category.csv",
            "- output/tables/ada_incidents_by_stop.csv",
            "- output/tables/ada_top15_stops.csv",
            "- output/tables/ada_incidents_by_responsible_party.csv",
            "- output/figures/ada_incidents_by_year_bar.png",
            "- output/figures/ada_top15_stops_bar.png",
        ]
    )

    (OUTPUT_REPORTS / "ADA_Incident_Analysis.md").write_text("\n".join(lines), encoding="utf-8")

    print("ADA incident analysis completed.")
    print(f"Total incidents: {total} | Unresolved: {unresolved} ({unresolved_rate}%)")


if __name__ == "__main__":
    main()
