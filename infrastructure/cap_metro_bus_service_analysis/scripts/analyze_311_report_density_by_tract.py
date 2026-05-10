"""
analyze_311_report_density_by_tract.py

Calculates 311 Service Request Report Density per Census Tract for
fiscal years FY2022–FY2026 (scope: 2021-10-01 through 2026-04-17).

Dataset: Austin Transportation and Public Works 311 Service Requests
(archive/legacy/Austin_311_Public_Data_20260412.csv)

Outputs
-------
output/tables/311_report_density_by_tract.csv        — per-tract full results
output/tables/311_report_density_by_district.csv     — council-district summary
output/tables/311_report_density_top25_tracts.csv    — top 25 tracts by density
output/tables/311_digital_divide_by_method.csv       — method breakdown by district
output/figures/311_report_density_top25.png          — bar chart top 25 tracts
output/figures/311_digital_divide_by_district.png    — stacked method breakdown
output/figures/311_report_density_yearly_trend.png   — FY-by-FY trend by district
output/figures/311_annual_volume_by_district_heatmap.png — annual volume heatmap by district
output/figures/311_annual_volume_priority_districts_heatmap.png — annual heatmap for priority districts only
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parent.parent

# ── paths ────────────────────────────────────────────────────────────────────
RAW_311 = ROOT / "archive" / "legacy" / "Austin_311_Public_Data_20260412.csv"
TRACT_GEO = ROOT / "data" / "geo" / "census_tracts.geojson"
MSA_CSV = ROOT / "archive" / "sources" / "austin_msa_5_county_tract_redistricting_2020_2026_04_17.csv"

OUT_TABLES = ROOT / "output" / "tables"
OUT_FIGS   = ROOT / "output" / "figures"
OUT_TABLES.mkdir(parents=True, exist_ok=True)
OUT_FIGS.mkdir(parents=True, exist_ok=True)

# ── palette (USWDS government) ────────────────────────────────────────────────
NAVY   = "#1a3a5c"
GREEN  = "#2e8540"
YELLOW = "#fdb81e"
ORANGE = "#e66000"
RED    = "#cc0000"
SLATE  = "#5b616b"
BG     = "#f5f7fa"

# ── scope ─────────────────────────────────────────────────────────────────────
FY_START = pd.Timestamp("2021-10-01")
FY_END   = pd.Timestamp("2026-04-17")

# Travis County FIPS = 453; include Williamson (491), Hays (209), Bastrop (021),
# Caldwell (055) for full Austin MSA; but restrict spatial join to Travis County
TRAVIS_COUNTY_FP = "453"

# Digital divide: classify methods
PHONE_METHODS   = {"Phone"}
DIGITAL_METHODS = {"Spot311 Interface", "Web", "Mobile Device", "Citizen Web Intake"}


# ─────────────────────────────────────────────────────────────────────────────
# 1.  Load census tract centroids (Travis County only)
# ─────────────────────────────────────────────────────────────────────────────
def load_tract_centroids() -> pd.DataFrame:
    with open(TRACT_GEO) as f:
        gj = json.load(f)
    rows = []
    for feat in gj["features"]:
        p = feat["properties"]
        if p.get("countyfp") != TRAVIS_COUNTY_FP:
            continue
        rows.append(
            {
                "geoid": p["geoid"],
                "tract_name": p["namelsad"],
                "tractce": p["tractce"],
                "centroid_lat": float(p["intptlat"]),
                "centroid_lon": float(p["intptlon"]),
                "aland_sqm": float(p.get("aland", 0) or 0),
            }
        )
    df = pd.DataFrame(rows)
    df["aland_sqkm"] = df["aland_sqm"] / 1_000_000
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2.  Load population (2020 Census POP100 per tract)
# ─────────────────────────────────────────────────────────────────────────────
def load_tract_population() -> pd.DataFrame:
    raw = pd.read_csv(MSA_CSV, dtype=str, low_memory=False)
    # Keep tract-level rows (SUMLEV == 140) in Travis County (COUNTY == 453)
    raw["SUMLEV"] = raw["SUMLEV"].astype(str).str.strip()
    raw["COUNTY"] = raw["COUNTY"].astype(str).str.strip().str.zfill(3)
    tract_rows = raw[(raw["SUMLEV"] == "140") & (raw["COUNTY"] == "453")].copy()
    tract_rows["pop2020"] = (
        tract_rows["POP100"]
        .str.replace(",", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0)
        .astype(int)
    )
    # Build geoid: statefp(2) + countyfp(3) + tractce(6)
    tract_rows["geoid"] = (
        tract_rows["STATE"].str.zfill(2)
        + tract_rows["COUNTY"].str.zfill(3)
        + tract_rows["TRACT"].str.zfill(6)
    )
    return tract_rows[["geoid", "pop2020"]].drop_duplicates("geoid")


# ─────────────────────────────────────────────────────────────────────────────
# 3.  Load & filter 311 data
# ─────────────────────────────────────────────────────────────────────────────
USECOLS = [
    "Created Date",
    "Method Received",
    "SR Status",
    "Council District",
    "Latitude Coordinate",
    "Longitude Coordinate",
]

def load_311() -> pd.DataFrame:
    chunks = []
    for chunk in pd.read_csv(
        RAW_311,
        chunksize=100_000,
        low_memory=False,
        usecols=USECOLS,
    ):
        chunk["dt"] = pd.to_datetime(chunk["Created Date"], errors="coerce")
        # Filter to fiscal year scope
        chunk = chunk[(chunk["dt"] >= FY_START) & (chunk["dt"] <= FY_END)]
        # Drop rows without coordinates
        chunk = chunk.dropna(subset=["Latitude Coordinate", "Longitude Coordinate"])
        # Rough Travis County bounding box (lat 30.05–30.65, lon –98.1 to –97.4)
        chunk = chunk[
            (chunk["Latitude Coordinate"].between(30.05, 30.65))
            & (chunk["Longitude Coordinate"].between(-98.1, -97.4))
        ]
        if len(chunk):
            chunks.append(chunk)
    df = pd.concat(chunks, ignore_index=True)
    df["fy"] = df["dt"].apply(
        lambda d: d.year if d.month >= 10 else d.year - 1
    )  # fiscal year label: Oct–Sep window, labelled by start year
    df["method_class"] = df["Method Received"].apply(
        lambda m: "Phone" if m in PHONE_METHODS
        else ("Digital" if m in DIGITAL_METHODS else "Other")
    )
    df["council_district"] = (
        pd.to_numeric(df["Council District"], errors="coerce").fillna(0).astype(int)
    )
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 4.  Assign each 311 record to nearest tract centroid (KD-tree)
# ─────────────────────────────────────────────────────────────────────────────
def assign_tracts(df: pd.DataFrame, centroids: pd.DataFrame) -> pd.DataFrame:
    # KD-tree on (lat, lon) of tract centroids
    # Use degree-scale distances (small enough for a single metro area)
    tree_coords = centroids[["centroid_lat", "centroid_lon"]].to_numpy()
    tree = cKDTree(tree_coords)

    pts = df[["Latitude Coordinate", "Longitude Coordinate"]].to_numpy()
    _, idx = tree.query(pts, k=1, workers=-1)  # workers=-1 uses all CPU cores

    df = df.copy()
    df["tract_idx"] = idx
    df["geoid"] = centroids["geoid"].iloc[idx].values
    df["tract_name"] = centroids["tract_name"].iloc[idx].values
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 5.  Aggregate
# ─────────────────────────────────────────────────────────────────────────────
def build_tract_summary(
    df: pd.DataFrame, centroids: pd.DataFrame, pop: pd.DataFrame
) -> pd.DataFrame:
    totals = df.groupby("geoid").size().rename("total_reports").reset_index()
    phone = df[df["method_class"] == "Phone"].groupby("geoid").size().rename("phone_reports").reset_index()
    digital = df[df["method_class"] == "Digital"].groupby("geoid").size().rename("digital_reports").reset_index()

    summary = (
        centroids[["geoid", "tract_name", "aland_sqkm"]]
        .merge(totals, on="geoid", how="left")
        .merge(phone, on="geoid", how="left")
        .merge(digital, on="geoid", how="left")
        .merge(pop, on="geoid", how="left")
    )
    summary[["total_reports", "phone_reports", "digital_reports"]] = (
        summary[["total_reports", "phone_reports", "digital_reports"]].fillna(0).astype(int)
    )
    summary["pop2020"] = summary["pop2020"].fillna(0).astype(int)
    summary["other_reports"] = (
        summary["total_reports"] - summary["phone_reports"] - summary["digital_reports"]
    ).clip(lower=0)

    # Density metrics
    summary["reports_per_1000_residents"] = np.where(
        summary["pop2020"] > 0,
        (summary["total_reports"] / summary["pop2020"] * 1000).round(1),
        np.nan,
    )
    summary["reports_per_sqkm"] = np.where(
        summary["aland_sqkm"] > 0,
        (summary["total_reports"] / summary["aland_sqkm"]).round(1),
        np.nan,
    )
    summary["pct_phone"] = np.where(
        summary["total_reports"] > 0,
        (summary["phone_reports"] / summary["total_reports"] * 100).round(1),
        np.nan,
    )
    summary["pct_digital"] = np.where(
        summary["total_reports"] > 0,
        (summary["digital_reports"] / summary["total_reports"] * 100).round(1),
        np.nan,
    )
    return summary.sort_values("total_reports", ascending=False)


def build_district_summary(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby(["council_district", "method_class"]).size().unstack(fill_value=0)
    grp.columns.name = None
    for col in ["Phone", "Digital", "Other"]:
        if col not in grp.columns:
            grp[col] = 0
    grp["total"] = grp[["Phone", "Digital", "Other"]].sum(axis=1)
    grp["pct_phone"] = (grp["Phone"] / grp["total"] * 100).round(1)
    grp["pct_digital"] = (grp["Digital"] / grp["total"] * 100).round(1)
    return grp.reset_index().rename(columns={"council_district": "council_district"})


def build_yearly_trend(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["fy", "council_district"])
        .size()
        .rename("reports")
        .reset_index()
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6.  Figures
# ─────────────────────────────────────────────────────────────────────────────
def fig_top25(tract_df: pd.DataFrame) -> None:
    top = tract_df.dropna(subset=["reports_per_1000_residents"]).nlargest(25, "reports_per_1000_residents")
    labels = top["tract_name"].str.replace("Census Tract ", "Tract ", regex=False)
    colors = [
        RED if r > 2000 else ORANGE if r > 1000 else YELLOW if r > 500 else GREEN
        for r in top["reports_per_1000_residents"]
    ]

    fig, axes = plt.subplots(1, 2, figsize=(18, 9), facecolor=BG)
    fig.suptitle(
        "311 Report Density by Census Tract — Austin (FY2022–FY2026 YTD)",
        fontsize=14, fontweight="bold", color=NAVY, y=0.98,
    )

    # left: reports per 1,000 residents
    ax1 = axes[0]
    ax1.set_facecolor(BG)
    bars = ax1.barh(labels[::-1], top["reports_per_1000_residents"][::-1], color=colors[::-1], edgecolor="white")
    ax1.set_xlabel("Reports per 1,000 Residents (2020 Pop.)", color=SLATE, fontsize=10)
    ax1.set_title("Density by Population", color=NAVY, fontsize=12, fontweight="bold")
    ax1.tick_params(axis="y", labelsize=8, colors=SLATE)
    ax1.tick_params(axis="x", colors=SLATE)
    ax1.spines[["top", "right", "left"]].set_visible(False)
    ax1.grid(axis="x", alpha=0.3, color=SLATE)
    for bar, val in zip(bars[::-1], top["reports_per_1000_residents"]):
        ax1.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                 f"{val:,.0f}", va="center", ha="left", fontsize=7, color=SLATE)

    # right: reports per sq km
    top2 = tract_df.dropna(subset=["reports_per_sqkm"]).nlargest(25, "reports_per_sqkm")
    labels2 = top2["tract_name"].str.replace("Census Tract ", "Tract ", regex=False)
    colors2 = [
        RED if r > 5000 else ORANGE if r > 2000 else YELLOW if r > 1000 else GREEN
        for r in top2["reports_per_sqkm"]
    ]
    ax2 = axes[1]
    ax2.set_facecolor(BG)
    bars2 = ax2.barh(labels2[::-1], top2["reports_per_sqkm"][::-1], color=colors2[::-1], edgecolor="white")
    ax2.set_xlabel("Reports per km² (land area)", color=SLATE, fontsize=10)
    ax2.set_title("Density by Land Area", color=NAVY, fontsize=12, fontweight="bold")
    ax2.tick_params(axis="y", labelsize=8, colors=SLATE)
    ax2.tick_params(axis="x", colors=SLATE)
    ax2.spines[["top", "right", "left"]].set_visible(False)
    ax2.grid(axis="x", alpha=0.3, color=SLATE)
    for bar, val in zip(bars2[::-1], top2["reports_per_sqkm"]):
        ax2.text(bar.get_width() + 20, bar.get_y() + bar.get_height() / 2,
                 f"{val:,.0f}", va="center", ha="left", fontsize=7, color=SLATE)

    fig.text(0.5, 0.01,
             "Source: Austin 311 Service Requests (Oct 2021–Apr 2026). "
             "Population: 2020 Census. Tracts: Travis County only.",
             ha="center", fontsize=7, color=SLATE)
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    out = OUT_FIGS / "311_report_density_top25.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


def fig_digital_divide(district_df: pd.DataFrame) -> None:
    d = district_df[district_df["council_district"] > 0].sort_values("council_district")
    districts = [f"District {int(x)}" for x in d["council_district"]]
    phone_pct = d["pct_phone"].values
    digital_pct = d["pct_digital"].values
    other_pct = (100 - phone_pct - digital_pct).clip(0)

    x = np.arange(len(districts))
    width = 0.6

    fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
    ax.set_facecolor(BG)
    p1 = ax.bar(x, phone_pct, width, label="Phone", color=NAVY)
    p2 = ax.bar(x, digital_pct, width, bottom=phone_pct, label="Digital (App/Web)", color=GREEN)
    p3 = ax.bar(x, other_pct, width, bottom=phone_pct + digital_pct, label="Other/Unknown", color=SLATE, alpha=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(districts, fontsize=10, color=SLATE)
    ax.set_ylabel("% of 311 Reports", color=SLATE, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_title(
        "Digital Divide: 311 Report Method by Council District (FY2022–FY2026 YTD)",
        fontsize=13, fontweight="bold", color=NAVY,
    )
    ax.legend(fontsize=9, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3, color=SLATE)
    ax.tick_params(axis="y", colors=SLATE)

    # Annotate phone % on bars
    for xi, (pp, dp) in enumerate(zip(phone_pct, digital_pct)):
        ax.text(xi, pp / 2, f"{pp:.0f}%", ha="center", va="center", fontsize=8,
                color="white", fontweight="bold")
        ax.text(xi, pp + dp / 2, f"{dp:.0f}%", ha="center", va="center", fontsize=8,
                color="white", fontweight="bold")

    fig.text(0.5, 0.01,
             "Source: Austin 311 Service Requests (Oct 2021–Apr 2026). "
             "'Digital' = Spot311 app, Web, Mobile, Citizen Web Intake.",
             ha="center", fontsize=7, color=SLATE)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    out = OUT_FIGS / "311_digital_divide_by_district.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


def fig_yearly_trend(trend_df: pd.DataFrame) -> None:
    core_districts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    d = trend_df[trend_df["council_district"].isin(core_districts)]
    pivot = d.pivot_table(index="fy", columns="council_district", values="reports", aggfunc="sum").fillna(0)

    colors_map = [NAVY, "#2980b9", GREEN, "#27ae60", ORANGE, YELLOW, RED, "#8e44ad", SLATE, "#c0392b"]

    fig, ax = plt.subplots(figsize=(14, 7), facecolor=BG)
    ax.set_facecolor(BG)
    for i, dist in enumerate(core_districts):
        if dist in pivot.columns:
            ax.plot(
                pivot.index,
                pivot[dist],
                marker="o",
                label=f"D{dist}",
                color=colors_map[i % len(colors_map)],
                linewidth=2,
            )

    ax.set_xlabel("Fiscal Year (Oct–Sep, FY2026 = partial through Apr 2026)", color=SLATE, fontsize=10)
    ax.set_ylabel("Total 311 Reports", color=SLATE, fontsize=10)
    ax.set_title(
        "Annual 311 Report Volume by Council District (FY2022–FY2026 YTD)",
        fontsize=13, fontweight="bold", color=NAVY,
    )
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.legend(title="District", fontsize=9, ncol=2, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.3, color=SLATE)
    ax.tick_params(colors=SLATE)

    fig.text(0.5, 0.01,
             "Source: Austin 311 Service Requests. FY label = start year (e.g., FY2021 = Oct 2021–Sep 2022). "
             "FY2025 = Oct 2025–Apr 2026 (partial).",
             ha="center", fontsize=7, color=SLATE)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    out = OUT_FIGS / "311_report_density_yearly_trend.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


def fig_yearly_heatmap(trend_df: pd.DataFrame) -> None:
    """Simpler annual view: heatmap of report counts by district and fiscal year."""
    core_districts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    d = trend_df[trend_df["council_district"].isin(core_districts)].copy()

    pivot = (
        d.pivot_table(index="council_district", columns="fy", values="reports", aggfunc="sum")
        .reindex(core_districts)
        .fillna(0)
        .astype(int)
    )

    fig, ax = plt.subplots(figsize=(11, 6.8), facecolor=BG)
    ax.set_facecolor(BG)

    heat = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")
    cbar = fig.colorbar(heat, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label("311 report count", color=SLATE)
    cbar.ax.yaxis.set_tick_params(color=SLATE)
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color=SLATE)

    x_labels = [f"FY{int(y) + 1}" for y in pivot.columns]
    y_labels = [f"District {int(dy)}" for dy in pivot.index]
    ax.set_xticks(np.arange(len(x_labels)))
    ax.set_xticklabels(x_labels, color=SLATE)
    ax.set_yticks(np.arange(len(y_labels)))
    ax.set_yticklabels(y_labels, color=SLATE)

    # Add count labels inside cells; switch text color based on intensity.
    max_val = max(1, pivot.values.max())
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = int(pivot.iloc[i, j])
            text_color = "white" if val > 0.55 * max_val else NAVY
            ax.text(j, i, f"{val:,}", ha="center", va="center", fontsize=8, color=text_color)

    ax.set_title(
        "Annual 311 Report Volume by Council District (Heatmap)\nFY2026 is partial through Apr 2026",
        fontsize=13,
        fontweight="bold",
        color=NAVY,
    )
    ax.set_xlabel("Fiscal year", color=SLATE)
    ax.set_ylabel("Council district", color=SLATE)

    ax.set_xticks(np.arange(-0.5, len(x_labels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(y_labels), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=0.8)
    ax.tick_params(which="minor", bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.text(
        0.5,
        0.01,
        "Source: Austin 311 Service Requests. FY labels use Oct-Sep windows; FY2026 is partial.",
        ha="center",
        fontsize=7,
        color=SLATE,
    )
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    out = OUT_FIGS / "311_annual_volume_by_district_heatmap.png"
    plt.savefig(out, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


def fig_yearly_heatmap_priority(trend_df: pd.DataFrame) -> None:
    """High-clarity annual view for priority districts only."""
    priority_districts = [3, 4, 5, 7, 9]
    d = trend_df[trend_df["council_district"].isin(priority_districts)].copy()

    pivot = (
        d.pivot_table(index="council_district", columns="fy", values="reports", aggfunc="sum")
        .reindex(priority_districts)
        .fillna(0)
        .astype(int)
    )

    fig, ax = plt.subplots(figsize=(9.5, 5.2), facecolor=BG)
    ax.set_facecolor(BG)

    heat = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")
    cbar = fig.colorbar(heat, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label("311 report count", color=SLATE)
    cbar.ax.yaxis.set_tick_params(color=SLATE)
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color=SLATE)

    x_labels = [f"FY{int(y) + 1}" for y in pivot.columns]
    y_labels = [f"District {int(dy)}" for dy in pivot.index]
    ax.set_xticks(np.arange(len(x_labels)))
    ax.set_xticklabels(x_labels, color=SLATE)
    ax.set_yticks(np.arange(len(y_labels)))
    ax.set_yticklabels(y_labels, color=SLATE)

    max_val = max(1, pivot.values.max())
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = int(pivot.iloc[i, j])
            text_color = "white" if val > 0.55 * max_val else NAVY
            ax.text(j, i, f"{val:,}", ha="center", va="center", fontsize=9, color=text_color)

    ax.set_title(
        "Annual 311 Volume: Priority Districts (3, 4, 5, 7, 9)\nFY2026 is partial through Apr 2026",
        fontsize=13,
        fontweight="bold",
        color=NAVY,
    )
    ax.set_xlabel("Fiscal year", color=SLATE)
    ax.set_ylabel("Priority council district", color=SLATE)

    ax.set_xticks(np.arange(-0.5, len(x_labels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(y_labels), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=0.9)
    ax.tick_params(which="minor", bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.text(
        0.5,
        0.01,
        "Source: Austin 311 Service Requests. FY labels use Oct-Sep windows; FY2026 is partial.",
        ha="center",
        fontsize=7,
        color=SLATE,
    )
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    out = OUT_FIGS / "311_annual_volume_priority_districts_heatmap.png"
    plt.savefig(out, dpi=170, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


def fig_top_tracts_total(tract_df: pd.DataFrame) -> None:
    """Bar chart: top 25 tracts by absolute report count."""
    top = tract_df.nlargest(25, "total_reports")
    labels = top["tract_name"].str.replace("Census Tract ", "Tract ", regex=False)
    colors = [
        RED if r >= 20000 else ORANGE if r >= 10000 else YELLOW if r >= 5000 else GREEN
        for r in top["total_reports"]
    ]

    fig, ax = plt.subplots(figsize=(12, 9), facecolor=BG)
    ax.set_facecolor(BG)
    bars = ax.barh(labels[::-1], top["total_reports"][::-1], color=colors[::-1], edgecolor="white")
    ax.set_xlabel("Total 311 Reports (Oct 2021–Apr 2026)", color=SLATE, fontsize=10)
    ax.set_title(
        "Top 25 Census Tracts by Total 311 Volume — Travis County",
        fontsize=13, fontweight="bold", color=NAVY,
    )
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", alpha=0.3, color=SLATE)
    ax.tick_params(axis="y", labelsize=9, colors=SLATE)
    ax.tick_params(axis="x", colors=SLATE)
    for bar, val in zip(bars[::-1], top["total_reports"]):
        ax.text(bar.get_width() + 100, bar.get_y() + bar.get_height() / 2,
                f"{val:,}", va="center", ha="left", fontsize=8, color=SLATE)

    fig.text(0.5, 0.01,
             "Source: Austin 311 Service Requests (Oct 2021–Apr 2026). Travis County tracts only.",
             ha="center", fontsize=7, color=SLATE)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    out = OUT_FIGS / "311_top25_tracts_total_volume.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    print("Loading census tract centroids…")
    centroids = load_tract_centroids()
    print(f"  Travis County tracts: {len(centroids)}")

    print("Loading 2020 Census population…")
    pop = load_tract_population()
    print(f"  Population rows: {len(pop)}")

    print("Loading and filtering 311 data (FY2022–FY2026)…")
    df311 = load_311()
    print(f"  311 records in scope: {len(df311):,}")

    print("Assigning census tracts via KD-tree nearest centroid…")
    df311 = assign_tracts(df311, centroids)
    print("  Tract assignment complete.")

    print("Aggregating…")
    tract_df = build_tract_summary(df311, centroids, pop)
    district_df = build_district_summary(df311)
    trend_df = build_yearly_trend(df311)
    top25 = tract_df.nlargest(25, "reports_per_1000_residents")

    # ── save tables ──────────────────────────────────────────────────────────
    tract_out = OUT_TABLES / "311_report_density_by_tract.csv"
    district_out = OUT_TABLES / "311_report_density_by_district.csv"
    top25_out = OUT_TABLES / "311_report_density_top25_tracts.csv"
    method_out = OUT_TABLES / "311_digital_divide_by_method.csv"

    tract_df.to_csv(tract_out, index=False)
    district_df.to_csv(district_out, index=False)
    top25.to_csv(top25_out, index=False)
    trend_df.to_csv(method_out, index=False)
    print(f"Saved {tract_out}")
    print(f"Saved {district_out}")
    print(f"Saved {top25_out}")

    # ── summary stats ─────────────────────────────────────────────────────────
    active = tract_df[tract_df["total_reports"] > 0]
    print("\n=== SUMMARY ===")
    print(f"Total 311 reports in scope: {df311.shape[0]:,}")
    print(f"Tracts with any reports: {len(active)} / {len(tract_df)}")
    print(f"Mean reports per tract: {active['total_reports'].mean():.0f}")
    print(f"Median reports per tract: {active['total_reports'].median():.0f}")
    print(f"Max reports per tract: {active['total_reports'].max():,}  ({active.iloc[0]['tract_name']})")
    print(f"Mean density (per 1k pop): {tract_df['reports_per_1000_residents'].mean():.1f}")
    print(f"\nTop 10 tracts by reports/1k residents:")
    for _, r in top25.head(10).iterrows():
        print(f"  {r['tract_name']:35s}  {r['reports_per_1000_residents']:7.1f}/1k  "
              f"({r['total_reports']:,} reports, pop {r['pop2020']:,})")
    print(f"\nDigital divide (citywide):")
    total = df311.shape[0]
    phone_n = (df311["method_class"] == "Phone").sum()
    dig_n = (df311["method_class"] == "Digital").sum()
    print(f"  Phone:   {phone_n:,}  ({phone_n/total*100:.1f}%)")
    print(f"  Digital: {dig_n:,}  ({dig_n/total*100:.1f}%)")

    # ── figures ────────────────────────────────────────────────────────────────
    print("\nGenerating figures…")
    fig_top25(tract_df)
    fig_top_tracts_total(tract_df)
    fig_digital_divide(district_df)
    fig_yearly_trend(trend_df)
    fig_yearly_heatmap(trend_df)
    fig_yearly_heatmap_priority(trend_df)
    print("Done.")


if __name__ == "__main__":
    main()
