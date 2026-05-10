from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

import numpy as np
import pandas as pd
import yaml
from scipy.stats import linregress


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "analysis_config.yaml"
OUTPUT_TABLES = ROOT / "output" / "tables"


@dataclass
class AnalysisConfig:
    fiscal_years: list[int]
    ytd_year: int
    ytd_note: str
    weights: dict[str, float]
    files: dict[str, str]


def load_config(path: Path) -> AnalysisConfig:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return AnalysisConfig(
        fiscal_years=[int(x) for x in raw["timeframe"]["fiscal_years"]],
        ytd_year=int(raw["timeframe"]["ytd_year"]),
        ytd_note=str(raw["timeframe"]["ytd_note"]),
        weights=raw["weights"],
        files=raw["files"],
    )


def normalize_stop_name(value: str) -> str:
    text = str(value).strip().lower()
    text = text.replace(" station", "")
    text = re.sub(r"\(.*?\)", "", text)
    text = text.replace("&", "/")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_column(df: pd.DataFrame, candidates: Iterable[str]) -> str:
    lowered = {col.lower().strip(): col for col in df.columns}
    for candidate in candidates:
        key = candidate.lower().strip()
        if key in lowered:
            return lowered[key]

    for col in df.columns:
        col_norm = col.lower().strip()
        for candidate in candidates:
            if candidate.lower().strip() in col_norm:
                return col

    raise KeyError(f"None of the candidate columns were found: {list(candidates)}")


def parse_percent(x: object) -> float:
    if pd.isna(x):
        return np.nan
    text = str(x).replace("%", "").strip()
    if not text:
        return np.nan
    return float(text) / 100.0


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def min_max_scale(series: pd.Series) -> pd.Series:
    s = to_numeric(series).fillna(0)
    if s.max() == s.min():
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - s.min()) / (s.max() - s.min())


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def build_stop_baseline(cfg: AnalysisConfig) -> pd.DataFrame:
    high_priority = load_csv(ROOT / cfg.files["high_priority_stops"])
    complaints = load_csv(ROOT / cfg.files["complaints_summary"])
    equity = load_csv(ROOT / cfg.files["equity_summary"])

    high_priority["normalized_stop"] = high_priority["stop_name"].map(normalize_stop_name)

    complaints_stop_col = find_column(complaints, ["Stop Name", "stop_name"])
    complaints_total_col = find_column(
        complaints,
        ["Total Calls (2021-2025)", "Total Calls", "total_calls"],
    )
    complaints_safety_col = find_column(
        complaints,
        ["Safety Concerns", "Safety Concerns Reports", "safety"],
    )
    complaints["normalized_stop"] = complaints[complaints_stop_col].map(normalize_stop_name)
    complaints["total_calls"] = to_numeric(complaints[complaints_total_col])
    complaints["safety_concerns"] = to_numeric(complaints[complaints_safety_col])

    equity_stop_col = find_column(equity, ["Stop Name", "stop_name"])
    equity_age_col = find_column(equity, ["Avg Open Ticket Age (Days)", "Age Days", "open ticket age"])
    equity_resp_col = find_column(equity, ["Response Rate", "response_rate"])
    equity["normalized_stop"] = equity[equity_stop_col].map(normalize_stop_name)
    equity["avg_open_ticket_age_days"] = to_numeric(equity[equity_age_col])
    equity["response_rate"] = equity[equity_resp_col].map(parse_percent)

    merged = (
        high_priority.merge(
            complaints[["normalized_stop", "total_calls", "safety_concerns"]],
            on="normalized_stop",
            how="left",
        )
        .merge(
            equity[["normalized_stop", "avg_open_ticket_age_days", "response_rate"]],
            on="normalized_stop",
            how="left",
        )
        .copy()
    )

    merged["amenity_gap"] = to_numeric(merged.get("amenity_gap", 0)).fillna(0)
    merged["trip_count"] = to_numeric(merged.get("trip_count", 0)).fillna(0)
    merged["total_calls"] = to_numeric(merged["total_calls"]).fillna(0)
    merged["safety_concerns"] = to_numeric(merged["safety_concerns"]).fillna(0)
    merged["avg_open_ticket_age_days"] = to_numeric(merged["avg_open_ticket_age_days"]).fillna(0)

    amenity_gap_scaled = min_max_scale(merged["amenity_gap"])
    calls_scaled = min_max_scale(merged["total_calls"])
    safety_scaled = min_max_scale(merged["safety_concerns"])
    age_scaled = min_max_scale(merged["avg_open_ticket_age_days"])

    merged["risk_score"] = (
        amenity_gap_scaled * cfg.weights["amenity_gap_weight"]
        + calls_scaled * cfg.weights["complaints_weight"]
        + safety_scaled * cfg.weights["safety_weight"]
        + age_scaled * cfg.weights["age_weight"]
    )

    merged["missing_shelter"] = 1 - to_numeric(merged.get("shelter_present", 0)).clip(lower=0, upper=1)
    merged["missing_bench"] = 1 - to_numeric(merged.get("bench_present", 0)).clip(lower=0, upper=1)

    baseline_cols = [
        "stop_id",
        "stop_name",
        "trip_count",
        "amenity_gap",
        "missing_shelter",
        "missing_bench",
        "total_calls",
        "safety_concerns",
        "avg_open_ticket_age_days",
        "response_rate",
        "risk_score",
    ]
    baseline = merged[baseline_cols].sort_values("risk_score", ascending=False)
    baseline.to_csv(OUTPUT_TABLES / "stop_baseline_risk_index.csv", index=False)
    return baseline


def build_yearly_trends(cfg: AnalysisConfig) -> pd.DataFrame:
    yearly = load_csv(ROOT / cfg.files["yearly_categories"])

    year_col = find_column(yearly, ["Year"])
    year_total_col = find_column(yearly, ["Year Total", "Total", "year_total"])
    shelter_col = find_column(yearly, ["Shelter"])
    bench_col = find_column(yearly, ["Benches", "Bench"])
    weather_col = find_column(yearly, ["Weather", "Weather Exposure"])
    safety_col = find_column(yearly, ["Safety", "Safety (CapMetro/City)"])
    ada_col = find_column(yearly, ["Sidewalk/ADA", "ADA"])

    trends = (
        yearly.groupby(year_col, as_index=False)
        .agg(
            complaints_total=(year_total_col, "sum"),
            shelter_complaints=(shelter_col, "sum"),
            bench_complaints=(bench_col, "sum"),
            weather_complaints=(weather_col, "sum"),
            safety_complaints=(safety_col, "sum"),
            sidewalk_ada_complaints=(ada_col, "sum"),
        )
        .sort_values(year_col)
        .rename(columns={year_col: "year"})
    )

    trends["safety_share"] = np.where(
        trends["complaints_total"] > 0,
        trends["safety_complaints"] / trends["complaints_total"],
        0,
    )

    trends.to_csv(OUTPUT_TABLES / "yearly_complaint_trends.csv", index=False)
    return trends


def build_responsibility_summary(cfg: AnalysisConfig) -> pd.DataFrame:
    summary = load_csv(ROOT / cfg.files["responsibility_summary"])

    stop_col = find_column(summary, ["Stop Name", "stop_name"])
    total_col = find_column(summary, ["Total Calls", "Total Calls (2021-2025)"])
    cmta_col = find_column(summary, ["CapMetro Issues", "CapMetro"])
    coa_col = find_column(summary, ["City of Austin Issues", "City"])

    out = summary[[stop_col, total_col, cmta_col, coa_col]].copy()
    out.columns = ["stop_name", "total_calls", "capmetro_issues", "city_of_austin_issues"]
    out["capmetro_share"] = np.where(
        to_numeric(out["total_calls"]) > 0,
        to_numeric(out["capmetro_issues"]) / to_numeric(out["total_calls"]),
        0,
    )
    out["city_share"] = np.where(
        to_numeric(out["total_calls"]) > 0,
        to_numeric(out["city_of_austin_issues"]) / to_numeric(out["total_calls"]),
        0,
    )

    out.to_csv(OUTPUT_TABLES / "jurisdiction_responsibility_summary.csv", index=False)
    return out


def build_evidence_matrix(
    cfg: AnalysisConfig,
    baseline: pd.DataFrame,
    trends: pd.DataFrame,
    responsibility: pd.DataFrame,
) -> pd.DataFrame:
    ada = load_csv(ROOT / cfg.files["ada_dataset"])

    if len(trends) >= 2:
        slope = linregress(trends["year"], trends["complaints_total"]).slope
    else:
        slope = np.nan

    total_calls = int(baseline["total_calls"].sum())
    safety_calls = int(baseline["safety_concerns"].sum())
    missing_shelter_rate = float((baseline["missing_shelter"] > 0).mean())
    missing_bench_rate = float((baseline["missing_bench"] > 0).mean())
    cmta_share = float(to_numeric(responsibility["capmetro_issues"]).sum() / to_numeric(responsibility["total_calls"]).sum())
    coa_share = float(to_numeric(responsibility["city_of_austin_issues"]).sum() / to_numeric(responsibility["total_calls"]).sum())

    ada_year_col = find_column(ada, ["Year", "Created Date"])
    if "year" in ada_year_col.lower():
        ada_recent = ada[to_numeric(ada[ada_year_col]).isin(cfg.fiscal_years + [cfg.ytd_year])]
    else:
        parsed = pd.to_datetime(ada[ada_year_col], errors="coerce")
        ada_recent = ada[parsed.dt.year.isin(cfg.fiscal_years + [cfg.ytd_year])]

    matrix = pd.DataFrame(
        [
            {
                "audit_question": "Are high-demand stops adequately equipped?",
                "metric": "Share missing shelter",
                "value": round(missing_shelter_rate, 4),
                "source": cfg.files["high_priority_stops"],
                "note": "Computed from shelter_present among high-priority stops.",
            },
            {
                "audit_question": "Are high-demand stops adequately equipped?",
                "metric": "Share missing benches",
                "value": round(missing_bench_rate, 4),
                "source": cfg.files["high_priority_stops"],
                "note": "Computed from bench_present among high-priority stops.",
            },
            {
                "audit_question": "Are conditions improving over time?",
                "metric": "Complaint trend slope (calls/year)",
                "value": round(float(slope), 4) if pd.notna(slope) else np.nan,
                "source": cfg.files["yearly_categories"],
                "note": "Positive slope indicates worsening complaint trajectory.",
            },
            {
                "audit_question": "Are safety risks visible in public feedback?",
                "metric": "Safety complaint share",
                "value": round(safety_calls / total_calls, 4) if total_calls > 0 else 0,
                "source": cfg.files["complaints_summary"],
                "note": "Safety concerns as a share of total calls for analyzed high-priority stops.",
            },
            {
                "audit_question": "Are responsibilities aligned between agencies?",
                "metric": "CapMetro issue share",
                "value": round(cmta_share, 4),
                "source": cfg.files["responsibility_summary"],
                "note": "Issue attribution among summarized high-priority stops.",
            },
            {
                "audit_question": "Are responsibilities aligned between agencies?",
                "metric": "City of Austin issue share",
                "value": round(coa_share, 4),
                "source": cfg.files["responsibility_summary"],
                "note": "Issue attribution among summarized high-priority stops.",
            },
            {
                "audit_question": "Are there ADA/compliance warning signals?",
                "metric": "ADA-related complaints in baseline window",
                "value": int(len(ada_recent)),
                "source": cfg.files["ada_dataset"],
                "note": "Count of ADA-related complaint records in selected fiscal years + YTD.",
            },
        ]
    )

    matrix.to_csv(OUTPUT_TABLES / "evidence_matrix.csv", index=False)
    return matrix


def build_presentation_tables(
    baseline: pd.DataFrame,
    trends: pd.DataFrame,
    responsibility: pd.DataFrame,
    matrix: pd.DataFrame,
) -> None:
    top10 = baseline.nlargest(10, "risk_score").copy()
    top10_out = top10[
        [
            "stop_name",
            "trip_count",
            "total_calls",
            "safety_concerns",
            "amenity_gap",
            "missing_shelter",
            "missing_bench",
            "risk_score",
        ]
    ].copy()
    top10_out["missing_shelter"] = np.where(top10_out["missing_shelter"] > 0, "Yes", "No")
    top10_out["missing_bench"] = np.where(top10_out["missing_bench"] > 0, "Yes", "No")
    top10_out["risk_score"] = top10_out["risk_score"].round(3)
    top10_out.to_csv(OUTPUT_TABLES / "top10_high_risk_stops_table.csv", index=False)

    trends_out = trends.copy()
    for col in [
        "shelter_complaints",
        "bench_complaints",
        "weather_complaints",
        "safety_complaints",
        "sidewalk_ada_complaints",
    ]:
        trends_out[f"{col}_share"] = np.where(
            trends_out["complaints_total"] > 0,
            trends_out[col] / trends_out["complaints_total"],
            0,
        )
    trends_out.to_csv(OUTPUT_TABLES / "yearly_complaints_with_percentages.csv", index=False)

    resp_out = responsibility.nlargest(15, "total_calls").copy()
    resp_out["capmetro_share_percent"] = (resp_out["capmetro_share"] * 100).round(1)
    resp_out["city_share_percent"] = (resp_out["city_share"] * 100).round(1)
    resp_out.to_csv(OUTPUT_TABLES / "top15_responsibility_table.csv", index=False)

    kpi_out = matrix[["metric", "value", "note"]].copy()
    kpi_out.to_csv(OUTPUT_TABLES / "kpi_summary_for_slides.csv", index=False)


def main() -> None:
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    cfg = load_config(CONFIG_PATH)

    baseline = build_stop_baseline(cfg)
    trends = build_yearly_trends(cfg)
    responsibility = build_responsibility_summary(cfg)
    matrix = build_evidence_matrix(cfg, baseline, trends, responsibility)
    build_presentation_tables(baseline, trends, responsibility, matrix)

    print("Baseline analysis completed.")
    print(f"Rows in stop risk index: {len(baseline)}")
    print(f"Rows in yearly trends: {len(trends)}")
    print(f"Rows in evidence matrix: {len(matrix)}")
    print("Presentation tables generated.")


if __name__ == "__main__":
    main()
