from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "canonical"
TABLES = ROOT / "output" / "tables"
FIGURES = ROOT / "output" / "figures"

# USWDS-oriented palette used elsewhere in this workspace
NAVY = "#1a3a5c"
SLATE = "#5b616b"
BG = "#f5f7fa"
RC_GREEN = "#2e8540"
RC_YELLOW = "#fdb81e"
RC_ORANGE = "#e66000"
RC_RED = "#cc0000"
DARK_RED = "#8b0000"


def norm(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0.0)
    lo = float(values.min())
    hi = float(values.max())
    if hi <= lo:
        return pd.Series(np.zeros(len(values)), index=values.index, dtype=float)
    return (values - lo) / (hi - lo)


def load_capital_plan(stops: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Load agency capital plan data if available.

    Expected preferred file:
      - data/canonical/agency_capital_plan_stops.csv

    Preferred columns (one of these should exist):
      - planned_improvement_points (numeric)
      - planned_projects_count (numeric)

    If file is missing, a zero-plan proxy is used for all stops.
    """
    candidates = [
        ROOT / "data" / "canonical" / "agency_capital_plan_stops.csv",
        ROOT / "data" / "reference" / "agency_capital_plan_stops.csv",
        ROOT / "output" / "tables" / "agency_capital_plan_stops.csv",
    ]

    cap_path = next((p for p in candidates if p.exists()), None)
    if cap_path is None:
        fallback = pd.DataFrame(
            {
                "stop_name": stops["stop_name"].astype(str),
                "planned_improvement_points": 0.0,
                "capital_source": "no_capital_plan_file_found",
            }
        )
        return fallback, "no_capital_plan_file_found"

    cap = pd.read_csv(cap_path)
    col_map = {c.lower().strip(): c for c in cap.columns}

    stop_col = None
    for candidate in ["stop_name", "stop", "station_name", "location_name"]:
        if candidate in col_map:
            stop_col = col_map[candidate]
            break
    if stop_col is None:
        fallback = pd.DataFrame(
            {
                "stop_name": stops["stop_name"].astype(str),
                "planned_improvement_points": 0.0,
                "capital_source": f"invalid_capital_file_missing_stop_name:{cap_path.name}",
            }
        )
        return fallback, f"invalid_capital_file_missing_stop_name:{cap_path.name}"

    if "planned_improvement_points" in col_map:
        plan_col = col_map["planned_improvement_points"]
        points = pd.to_numeric(cap[plan_col], errors="coerce").fillna(0.0)
    elif "planned_projects_count" in col_map:
        plan_col = col_map["planned_projects_count"]
        points = pd.to_numeric(cap[plan_col], errors="coerce").fillna(0.0)
    else:
        # If expected plan columns are missing, use zero points but keep provenance.
        points = pd.Series(np.zeros(len(cap)), index=cap.index, dtype=float)

    cleaned = pd.DataFrame(
        {
            "stop_name": cap[stop_col].astype(str).str.strip(),
            "planned_improvement_points": points,
            "capital_source": cap_path.name,
        }
    )

    return cleaned, cap_path.name


def build_gap_by_stop() -> Tuple[pd.DataFrame, str]:
    stops = pd.read_csv(DATA / "top_25_with_amenities.csv")
    tickets = pd.read_csv(DATA / "311_detailed_complaint_report.csv")

    stops = stops.copy()
    stops["stop_name"] = stops["stop_name"].astype(str).str.strip()

    ticket_work = tickets.copy()
    ticket_work["Stop Name"] = ticket_work["Stop Name"].astype(str).str.strip()
    ticket_work["Status"] = ticket_work["Status"].astype(str)
    ticket_work["Category"] = ticket_work["Category"].astype(str)

    demand = ticket_work.groupby("Stop Name", as_index=False).agg(
        total_311_reports=("SR Number", "count"),
        open_311_reports=("Status", lambda s: (s.str.lower() == "open").sum()),
        closed_311_reports=("Status", lambda s: (s.str.lower() == "closed").sum()),
    )

    safety_mask = ticket_work["Category"].str.contains(
        "Safety|ADA|Sidewalk|Weather", case=False, na=False
    )
    safety = (
        ticket_work[safety_mask]
        .groupby("Stop Name", as_index=False)
        .agg(safety_related_reports=("SR Number", "count"))
    )

    gap = stops.merge(
        demand,
        left_on="stop_name",
        right_on="Stop Name",
        how="left",
    )
    gap = gap.merge(
        safety,
        left_on="stop_name",
        right_on="Stop Name",
        how="left",
        suffixes=("", "_safety"),
    )

    gap["total_311_reports"] = pd.to_numeric(gap["total_311_reports"], errors="coerce").fillna(0)
    gap["open_311_reports"] = pd.to_numeric(gap["open_311_reports"], errors="coerce").fillna(0)
    gap["closed_311_reports"] = pd.to_numeric(gap["closed_311_reports"], errors="coerce").fillna(0)
    gap["safety_related_reports"] = pd.to_numeric(gap["safety_related_reports"], errors="coerce").fillna(0)

    gap["unresolved_rate"] = np.where(
        gap["total_311_reports"] > 0,
        gap["open_311_reports"] / gap["total_311_reports"],
        0.0,
    )

    gap["safety_share"] = np.where(
        gap["total_311_reports"] > 0,
        gap["safety_related_reports"] / gap["total_311_reports"],
        0.0,
    )

    # Demand side (community demand intensity from 311 behavior)
    gap["demand_index"] = (
        0.50 * norm(gap["total_311_reports"])
        + 0.30 * gap["unresolved_rate"].clip(0, 1)
        + 0.20 * norm(gap["safety_related_reports"])
    )

    # Existing service side (frequency proxy)
    gap["service_index"] = norm(gap["trip_count"]) 

    # Existing physical supply side (bench/shelter at stop)
    gap["existing_infra_index"] = (
        pd.to_numeric(gap["bench_present"], errors="coerce").fillna(0)
        + pd.to_numeric(gap["shelter_present"], errors="coerce").fillna(0)
    ) / 2.0

    # Planned capital supply side
    capital, capital_source = load_capital_plan(gap[["stop_name"]].copy())
    gap = gap.merge(
        capital[["stop_name", "planned_improvement_points", "capital_source"]],
        on="stop_name",
        how="left",
    )
    gap["planned_improvement_points"] = pd.to_numeric(
        gap["planned_improvement_points"], errors="coerce"
    ).fillna(0)
    gap["planned_supply_index"] = norm(gap["planned_improvement_points"]) 

    # Composite supply combines existing service, existing infrastructure, and planned supply.
    gap["supply_index"] = (
        0.50 * gap["service_index"]
        + 0.30 * gap["existing_infra_index"]
        + 0.20 * gap["planned_supply_index"]
    )

    # Primary gap metric: unmet demand above available/planned supply.
    gap["gap_score"] = gap["demand_index"] - gap["supply_index"]
    gap["gap_index_100"] = (gap["gap_score"] * 100).round(1)

    def label_gap(value: float) -> str:
        if value >= 25:
            return "SEVERE GAP"
        if value >= 10:
            return "HIGH GAP"
        if value >= 0:
            return "MODERATE GAP"
        return "LOWER GAP"

    gap["gap_priority"] = gap["gap_index_100"].apply(label_gap)

    # Attach district for district-level aggregation
    district_path = TABLES / "stop_geospatial_equity.csv"
    if district_path.exists():
        district = pd.read_csv(district_path)
        district = district[["stop_name", "council_district"]].drop_duplicates()
        gap = gap.merge(district, on="stop_name", how="left")
    else:
        gap["council_district"] = np.nan

    out_cols = [
        "stop_id",
        "stop_name",
        "council_district",
        "trip_count",
        "amenity_gap",
        "bench_present",
        "shelter_present",
        "total_311_reports",
        "open_311_reports",
        "closed_311_reports",
        "unresolved_rate",
        "safety_related_reports",
        "safety_share",
        "planned_improvement_points",
        "demand_index",
        "service_index",
        "existing_infra_index",
        "planned_supply_index",
        "supply_index",
        "gap_score",
        "gap_index_100",
        "gap_priority",
        "capital_source",
    ]

    out = gap[out_cols].copy().sort_values("gap_index_100", ascending=False)
    return out, capital_source


def build_gap_by_district(gap_by_stop: pd.DataFrame) -> pd.DataFrame:
    work = gap_by_stop.copy()
    work["district_key"] = work["council_district"].astype(str).str.strip()
    work = work[work["district_key"].notna() & (work["district_key"] != "")]

    district = (
        work.groupby("district_key", as_index=False)
        .agg(
            stops=("stop_name", "nunique"),
            total_311_reports=("total_311_reports", "sum"),
            open_311_reports=("open_311_reports", "sum"),
            total_trip_count=("trip_count", "sum"),
            avg_demand_index=("demand_index", "mean"),
            avg_supply_index=("supply_index", "mean"),
            avg_gap_index_100=("gap_index_100", "mean"),
            planned_improvement_points=("planned_improvement_points", "sum"),
        )
        .sort_values("avg_gap_index_100", ascending=False)
    )

    district = district.rename(columns={"district_key": "council_district"})
    district["district_gap_rank"] = (
        district["avg_gap_index_100"].rank(method="dense", ascending=False).astype(int)
    )
    return district


def make_figure(gap_by_stop: pd.DataFrame, gap_by_district: pd.DataFrame, fig_path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), facecolor=BG)
    fig.suptitle(
        "Gap Analysis: Community Demand vs Infrastructure Supply vs Service Frequency",
        fontsize=13,
        fontweight="bold",
        color=NAVY,
        y=0.98,
    )

    top = gap_by_stop.head(15).copy()

    # Panel A: Stop-level gap ranking
    ax = axes[0, 0]
    labels = top["stop_name"].astype(str)
    colors = [DARK_RED if v >= 25 else RC_RED if v >= 10 else RC_ORANGE if v >= 0 else RC_GREEN for v in top["gap_index_100"]]
    ax.barh(range(len(top)), top["gap_index_100"], color=colors)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(labels, fontsize=7)
    ax.invert_yaxis()
    ax.set_title("A. Highest Demand-Supply Gaps by Stop", fontsize=9, color=NAVY, fontweight="bold")
    ax.set_xlabel("Gap Index (Demand - Supply) x100", fontsize=8, color=SLATE)
    ax.tick_params(axis="x", labelsize=8, colors=SLATE)
    ax.tick_params(axis="y", labelsize=7, colors=SLATE)
    ax.axvline(0, color=SLATE, linewidth=1, linestyle="--")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    # Panel B: Demand vs Service scatter, bubble by planned points
    ax = axes[0, 1]
    bubble = (gap_by_stop["planned_improvement_points"].fillna(0) + 1) * 35
    sc = ax.scatter(
        gap_by_stop["service_index"],
        gap_by_stop["demand_index"],
        s=bubble,
        c=gap_by_stop["gap_index_100"],
        cmap="RdYlGn_r",
        alpha=0.85,
        edgecolor="white",
        linewidth=0.5,
    )
    ax.set_title("B. Demand vs Existing Service (Bubble = Planned Supply)", fontsize=9, color=NAVY, fontweight="bold")
    ax.set_xlabel("Service Index (frequency proxy)", fontsize=8, color=SLATE)
    ax.set_ylabel("Demand Index (311 intensity)", fontsize=8, color=SLATE)
    ax.tick_params(axis="both", labelsize=8, colors=SLATE)
    cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=7)
    cbar.set_label("Gap Index x100", fontsize=8)
    ax.grid(alpha=0.2)

    # Panel C: District average gap
    ax = axes[1, 0]
    if len(gap_by_district) > 0:
        d = gap_by_district.sort_values("avg_gap_index_100", ascending=False)
        d_labels = [f"D{str(v)}" for v in d["council_district"]]
        d_colors = [DARK_RED if v >= 25 else RC_RED if v >= 10 else RC_ORANGE if v >= 0 else RC_GREEN for v in d["avg_gap_index_100"]]
        ax.bar(d_labels, d["avg_gap_index_100"], color=d_colors)
        for i, val in enumerate(d["avg_gap_index_100"]):
            ax.text(i, val + 0.4, f"{val:.1f}", ha="center", va="bottom", fontsize=8, color=SLATE)
    ax.set_title("C. Average Gap by Council District", fontsize=9, color=NAVY, fontweight="bold")
    ax.set_ylabel("Average Gap Index x100", fontsize=8, color=SLATE)
    ax.tick_params(axis="both", labelsize=8, colors=SLATE)
    ax.axhline(0, color=SLATE, linewidth=1, linestyle="--")
    ax.grid(alpha=0.2, axis="y")

    # Panel D: Demand vs supply components (top 10)
    ax = axes[1, 1]
    t10 = gap_by_stop.head(10).copy()
    x = np.arange(len(t10))
    width = 0.28
    ax.bar(x - width, t10["demand_index"] * 100, width=width, color=RC_RED, label="Demand index")
    ax.bar(x, t10["service_index"] * 100, width=width, color=NAVY, label="Service index")
    ax.bar(x + width, t10["planned_supply_index"] * 100, width=width, color=RC_GREEN, label="Planned supply index")
    ax.set_xticks(x)
    ax.set_xticklabels([s[:18] + "..." if len(s) > 18 else s for s in t10["stop_name"]], rotation=40, ha="right", fontsize=7)
    ax.set_title("D. Top Stops: Demand vs Service vs Planned Supply", fontsize=9, color=NAVY, fontweight="bold")
    ax.set_ylabel("Normalized Index (0-100)", fontsize=8, color=SLATE)
    ax.tick_params(axis="y", labelsize=8, colors=SLATE)
    ax.legend(fontsize=7, loc="upper right")
    ax.grid(alpha=0.2, axis="y")

    fig.text(
        0.5,
        0.01,
        "Gap formula: demand_index = 0.50*norm(total_311_reports) + 0.30*unresolved_rate + 0.20*norm(safety_related_reports). "
        "supply_index = 0.50*service_index + 0.30*existing_infra_index + 0.20*planned_supply_index. "
        "gap_index = (demand_index - supply_index)*100. If no capital-plan file exists, planned supply defaults to 0.",
        ha="center",
        va="bottom",
        fontsize=7,
        color=SLATE,
    )

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig(fig_path, dpi=160, bbox_inches="tight", facecolor=BG)
    plt.close()


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    gap_by_stop, capital_source = build_gap_by_stop()
    gap_by_district = build_gap_by_district(gap_by_stop)

    stop_path = TABLES / "gap_analysis_by_stop.csv"
    district_path = TABLES / "gap_analysis_by_district.csv"
    summary_path = TABLES / "gap_analysis_summary.csv"
    figure_path = FIGURES / "gap_analysis_supply_demand.png"

    gap_by_stop.to_csv(stop_path, index=False)
    gap_by_district.to_csv(district_path, index=False)

    summary = pd.DataFrame(
        [
            {
                "metric": "capital_plan_source",
                "value": capital_source,
            },
            {
                "metric": "stops_analyzed",
                "value": int(len(gap_by_stop)),
            },
            {
                "metric": "severe_gap_stops",
                "value": int((gap_by_stop["gap_priority"] == "SEVERE GAP").sum()),
            },
            {
                "metric": "high_gap_stops",
                "value": int((gap_by_stop["gap_priority"] == "HIGH GAP").sum()),
            },
            {
                "metric": "top_gap_stop",
                "value": str(gap_by_stop.iloc[0]["stop_name"]) if len(gap_by_stop) else "",
            },
            {
                "metric": "top_gap_index_100",
                "value": float(gap_by_stop.iloc[0]["gap_index_100"]) if len(gap_by_stop) else 0.0,
            },
            {
                "metric": "district_with_highest_avg_gap",
                "value": str(gap_by_district.iloc[0]["council_district"]) if len(gap_by_district) else "",
            },
        ]
    )
    summary.to_csv(summary_path, index=False)

    make_figure(gap_by_stop, gap_by_district, figure_path)

    print("Gap analysis completed.")
    print(f"Saved: {stop_path}")
    print(f"Saved: {district_path}")
    print(f"Saved: {summary_path}")
    print(f"Saved: {figure_path}")


if __name__ == "__main__":
    main()
