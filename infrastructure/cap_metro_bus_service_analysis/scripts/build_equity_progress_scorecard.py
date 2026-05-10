from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "output" / "tables"
REPORTS = ROOT / "reports"
EXTERNAL_CLAIMS = ROOT / "data" / "external_reports" / "city_claims_from_external_analyses.csv"


def score_band(value: float, good_threshold: float, watch_threshold: float, higher_is_better: bool) -> str:
    if higher_is_better:
        if value >= good_threshold:
            return "Good"
        if value >= watch_threshold:
            return "Watch"
        return "Concern"

    if value <= good_threshold:
        return "Good"
    if value <= watch_threshold:
        return "Watch"
    return "Concern"


def main() -> None:
    kpi = pd.read_csv(TABLES / "kpi_summary_for_slides.csv")
    unresolved = pd.read_csv(TABLES / "311_unresolved_call_burden_by_stop.csv")
    ada_year = pd.read_csv(TABLES / "ada_incidents_by_year.csv")

    shelter_missing = float(kpi.loc[kpi["metric"] == "Share missing shelter", "value"].iloc[0])
    bench_missing = float(kpi.loc[kpi["metric"] == "Share missing benches", "value"].iloc[0])
    safety_share = float(kpi.loc[kpi["metric"] == "Safety complaint share", "value"].iloc[0])

    unresolved_rate_pct = float(
        pd.to_numeric(unresolved["unresolved_rate"], errors="coerce").fillna(0).mean()
    )

    ada_latest_year = int(ada_year["year"].max())
    ada_latest = ada_year.loc[ada_year["year"] == ada_latest_year].iloc[0]
    ada_unresolved_rate = float(ada_latest["unresolved_rate_pct"])

    scorecard = pd.DataFrame(
        [
            {
                "pillar": "A. Accessibility and ADA",
                "city_claim_focus": "ADA and accessible stop conditions are improving",
                "indicator": "ADA unresolved incident rate (latest year)",
                "value": round(ada_unresolved_rate, 1),
                "unit": "percent",
                "status": score_band(ada_unresolved_rate, good_threshold=20, watch_threshold=40, higher_is_better=False),
                "interpretation": "Lower is better. High values suggest unresolved accessibility burden.",
            },
            {
                "pillar": "B. Safety and Rider Conditions",
                "city_claim_focus": "Rider conditions are safer and better equipped",
                "indicator": "Missing shelter share at high-priority stops",
                "value": round(shelter_missing * 100, 1),
                "unit": "percent",
                "status": score_band(shelter_missing * 100, good_threshold=20, watch_threshold=40, higher_is_better=False),
                "interpretation": "Lower is better. High values indicate persistent exposure conditions.",
            },
            {
                "pillar": "B. Safety and Rider Conditions",
                "city_claim_focus": "Rider conditions are safer and better equipped",
                "indicator": "Safety complaint share",
                "value": round(safety_share * 100, 2),
                "unit": "percent",
                "status": score_band(safety_share * 100, good_threshold=5, watch_threshold=10, higher_is_better=False),
                "interpretation": "Lower is better. A high share indicates persistent safety signals.",
            },
            {
                "pillar": "C. Accountability and Resolution",
                "city_claim_focus": "Issues are being resolved quickly",
                "indicator": "Average unresolved 311 rate across analyzed stops",
                "value": round(unresolved_rate_pct, 1),
                "unit": "percent",
                "status": score_band(unresolved_rate_pct, good_threshold=20, watch_threshold=40, higher_is_better=False),
                "interpretation": "Lower is better. High values indicate closure lag.",
            },
            {
                "pillar": "C. Accountability and Resolution",
                "city_claim_focus": "Issues are being resolved quickly",
                "indicator": "Missing bench share at high-priority stops",
                "value": round(bench_missing * 100, 1),
                "unit": "percent",
                "status": score_band(bench_missing * 100, good_threshold=20, watch_threshold=40, higher_is_better=False),
                "interpretation": "Lower is better. High values indicate unresolved basic amenity deficits.",
            },
        ]
    )

    claims_note = "No external claim file found. Add data/external_reports/city_claims_from_external_analyses.csv to compare official claims against measured indicators."
    if EXTERNAL_CLAIMS.exists():
        claims_df = pd.read_csv(EXTERNAL_CLAIMS)
        claims_note = f"External claim file loaded with {len(claims_df)} row(s)."

    TABLES.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    scorecard.to_csv(TABLES / "equity_progress_scorecard.csv", index=False)

    lines = [
        "<!-- markdownlint-disable -->",
        "",
        "# Equity Progress Scorecard",
        "",
        "This scorecard compares public-facing progress themes against measured indicators from the baseline outputs.",
        "",
        "## Pillars",
        "",
        "- A: Accessibility and ADA",
        "- B: Safety and Rider Conditions",
        "- C: Accountability and Resolution",
        "",
        "## Scoring Labels",
        "",
        "- Good: favorable range",
        "- Watch: mixed signals",
        "- Concern: clear gap between claim and measured conditions",
        "",
        "## External Analyses Link",
        "",
        f"- {claims_note}",
        "",
        "## Output File",
        "",
        "- output/tables/equity_progress_scorecard.csv",
        "",
        "## Next Step",
        "",
        "Add external city-analysis claims to data/external_reports/city_claims_from_external_analyses.csv and rerun this script.",
    ]

    (REPORTS / "Equity_Progress_Scorecard.md").write_text("\n".join(lines), encoding="utf-8")

    print("Equity progress scorecard completed.")
    print("Wrote output/tables/equity_progress_scorecard.csv")


if __name__ == "__main__":
    main()
