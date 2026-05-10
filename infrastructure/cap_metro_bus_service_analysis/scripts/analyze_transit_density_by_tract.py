from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "output" / "tables"
REPORTS = ROOT / "reports"


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def format_council_district(value: object) -> str:
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return ""
    return text


def main() -> None:
    stop_geo_path = TABLES / "stop_geospatial_equity.csv"
    unresolved_path = TABLES / "311_unresolved_call_burden_by_stop.csv"

    if not stop_geo_path.exists():
        raise FileNotFoundError(
            "Missing output/tables/stop_geospatial_equity.csv. Run scripts/geospatial_equity_scaffold.py first."
        )

    stop_geo = pd.read_csv(stop_geo_path)

    required = ["stop_name", "council_district"]
    for col in required:
        if col not in stop_geo.columns:
            raise KeyError(f"Missing required column in stop_geospatial_equity.csv: {col}")

    work = stop_geo.copy()
    work["council_district"] = work["council_district"].map(format_council_district)
    work = work[work["council_district"].notna() & (work["council_district"] != "")]

    if "weekly_trips" in work.columns:
        work["weekly_trips"] = to_numeric(work["weekly_trips"]).fillna(0)
    else:
        work["weekly_trips"] = 0

    if "total_calls" in work.columns:
        work["total_calls"] = to_numeric(work["total_calls"]).fillna(0)
    else:
        work["total_calls"] = 0

    if "amenity_gap" in work.columns:
        work["amenity_gap"] = to_numeric(work["amenity_gap"]).fillna(0)
    else:
        work["amenity_gap"] = 0

    unresolved_by_stop = pd.DataFrame(columns=["stop_name", "unresolved_tickets"])
    if unresolved_path.exists():
        unresolved = pd.read_csv(unresolved_path)
        if {"stop_name", "unresolved_tickets"}.issubset(unresolved.columns):
            unresolved_by_stop = unresolved[["stop_name", "unresolved_tickets"]].copy()
            unresolved_by_stop["unresolved_tickets"] = to_numeric(
                unresolved_by_stop["unresolved_tickets"]
            ).fillna(0)

    work = work.merge(unresolved_by_stop, on="stop_name", how="left")
    work["unresolved_tickets"] = to_numeric(work["unresolved_tickets"]).fillna(0)

    tract_summary = (
        work.groupby("council_district", as_index=False)
        .agg(
            unique_stops=("stop_name", "nunique"),
            total_weekly_trips=("weekly_trips", "sum"),
            total_calls=("total_calls", "sum"),
            unresolved_tickets=("unresolved_tickets", "sum"),
            avg_amenity_gap=("amenity_gap", "mean"),
        )
        .sort_values(
            ["unique_stops", "total_calls", "unresolved_tickets"],
            ascending=[False, False, False],
        )
        .copy()
    )

    tract_summary["calls_per_stop"] = (
        tract_summary["total_calls"] / tract_summary["unique_stops"]
    ).round(2)
    tract_summary["unresolved_per_stop"] = (
        tract_summary["unresolved_tickets"] / tract_summary["unique_stops"]
    ).round(2)
    tract_summary["avg_amenity_gap"] = tract_summary["avg_amenity_gap"].round(2)

    tract_summary["transit_density_rank"] = (
        tract_summary["unique_stops"].rank(method="dense", ascending=False).astype(int)
    )

    out_cols = [
        "council_district",
        "transit_density_rank",
        "unique_stops",
        "total_weekly_trips",
        "total_calls",
        "unresolved_tickets",
        "calls_per_stop",
        "unresolved_per_stop",
        "avg_amenity_gap",
    ]
    out = tract_summary[out_cols].copy()

    TABLES.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    out.to_csv(TABLES / "transit_density_by_council_district.csv", index=False)
    out.head(15).to_csv(TABLES / "transit_density_top15_council_districts.csv", index=False)

    top = out.iloc[0]
    report_lines = [
        "<!-- markdownlint-disable -->",
        "",
        "# Transit Density by Council District",
        "",
        "This analysis computes transit density as unique analyzed stops per council district, then pairs density with complaint and unresolved burden.",
        "",
        "## Headline",
        "",
        f"- Highest-density council district in this run: {top['council_district']}",
        f"- Unique analyzed stops: {int(top['unique_stops'])}",
        f"- Total calls in council district: {int(top['total_calls'])}",
        f"- Unresolved tickets in council district: {int(top['unresolved_tickets'])}",
        "",
        "## Notes",
        "",
        "- This uses current analyzed stops, not the complete GTFS stop universe.",
        "- Use this as a council-district-level burden signal for equity discussions.",
        "- If you want full-system density, add full GTFS stops and rerun with complete stop geometry.",
        "",
        "## Output Files",
        "",
        "- output/tables/transit_density_by_council_district.csv",
        "- output/tables/transit_density_top15_council_districts.csv",
        "",
        "## External Benchmark Alignment",
        "",
        "Compare this council district output with external indexes (for example, Transit Propensity Index references from external reports) in your equity scorecard narrative.",
    ]

    (REPORTS / "Transit_Density_by_Tract.md").write_text("\n".join(report_lines), encoding="utf-8")

    print("Transit density by council district analysis completed.")
    print(f"Top council district: {top['council_district']} | Stops: {int(top['unique_stops'])}")


if __name__ == "__main__":
    main()
