"""
analyze_tract_stop_density_linkage.py

Links the 25 high-demand bus stops to their census tracts, enriches the
gap analysis and equity scorecard outputs with tract-level 311 density
data, and produces a combined figure set.

Outputs
-------
output/tables/stop_tract_density_linkage.csv       — per-stop tract + density enrichment
output/tables/gap_analysis_with_tract_density.csv  — gap analysis + tract density columns
output/tables/equity_tract_density_summary.csv     — tract density summary by council district
output/figures/stop_tract_density_scatter.png      — density vs gap index scatter
output/figures/stop_tract_density_combined.png     — 4-panel: density/gap/digital divide/district
output/figures/stop_tract_density_simple.png       — simple bar chart for slide use
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parent.parent

# ── paths ─────────────────────────────────────────────────────────────────────
TRACT_GEO         = ROOT / "data" / "geo" / "census_tracts.geojson"
STOP_AMENITIES    = ROOT / "data" / "canonical" / "stop_amenities_2026.csv"
TOP25             = ROOT / "data" / "canonical" / "top_25_with_amenities.csv"
GAP_BY_STOP       = ROOT / "output" / "tables" / "gap_analysis_by_stop.csv"
TRACT_DENSITY     = ROOT / "output" / "tables" / "311_report_density_by_tract.csv"
DISTRICT_DENSITY  = ROOT / "output" / "tables" / "311_report_density_by_district.csv"
PUBLIC_SAFETY     = ROOT / "output" / "tables" / "public_safety_risk_by_stop.csv"

OUT_TABLES = ROOT / "output" / "tables"
OUT_FIGS   = ROOT / "output" / "figures"
OUT_TABLES.mkdir(parents=True, exist_ok=True)
OUT_FIGS.mkdir(parents=True, exist_ok=True)

# ── palette ───────────────────────────────────────────────────────────────────
NAVY   = "#1a3a5c"
GREEN  = "#2e8540"
YELLOW = "#fdb81e"
ORANGE = "#e66000"
RED    = "#cc0000"
DARK_RED = "#8b0000"
SLATE  = "#5b616b"
BG     = "#f5f7fa"

TRAVIS_COUNTY_FP = "453"


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────
def load_tract_centroids() -> pd.DataFrame:
    with open(TRACT_GEO) as f:
        gj = json.load(f)
    rows = []
    for feat in gj["features"]:
        p = feat["properties"]
        if p.get("countyfp") != TRAVIS_COUNTY_FP:
            continue
        rows.append({
            "geoid": p["geoid"],
            "tract_name": p["namelsad"],
            "centroid_lat": float(p["intptlat"]),
            "centroid_lon": float(p["intptlon"]),
        })
    return pd.DataFrame(rows)


def assign_tracts_to_stops(stops: pd.DataFrame, centroids: pd.DataFrame) -> pd.Series:
    """Return a Series of geoid indexed by stops index."""
    tree = cKDTree(centroids[["centroid_lat", "centroid_lon"]].to_numpy())
    pts = stops[["lat", "lon"]].to_numpy()
    _, idx = tree.query(pts, k=1)
    return centroids["geoid"].iloc[idx].values


def gap_tier_color(tier: str) -> str:
    return {
        "SEVERE GAP": DARK_RED,
        "HIGH GAP": RED,
        "MODERATE GAP": ORANGE,
        "LOWER GAP": GREEN,
    }.get(tier, SLATE)


def risk_tier_color(score: float) -> str:
    if score >= 80:
        return DARK_RED
    if score >= 65:
        return RED
    if score >= 50:
        return ORANGE
    return GREEN


# ─────────────────────────────────────────────────────────────────────────────
# 1.  Build stop → tract → density linkage table
# ─────────────────────────────────────────────────────────────────────────────
def build_linkage() -> pd.DataFrame:
    # Stop coordinates
    sa = pd.read_csv(STOP_AMENITIES)[["STOP_ID", "LATITUDE", "LONGITUDE"]]
    sa.columns = ["stop_id", "lat", "lon"]

    t25 = pd.read_csv(TOP25)[["stop_id", "stop_name"]]
    stops = t25.merge(sa, on="stop_id", how="left")

    # Tract centroids
    centroids = load_tract_centroids()
    stops["geoid"] = assign_tracts_to_stops(stops, centroids)
    stops = stops.merge(centroids[["geoid", "tract_name"]], on="geoid", how="left")

    # Tract density
    td = pd.read_csv(TRACT_DENSITY, dtype={"geoid": str})
    stops["geoid"] = stops["geoid"].astype(str)
    stops = stops.merge(
        td[["geoid", "total_reports", "reports_per_1000_residents",
            "reports_per_sqkm", "pct_phone", "pct_digital", "pop2020"]],
        on="geoid", how="left",
    )
    stops.rename(columns={
        "total_reports": "tract_total_311_reports",
        "reports_per_1000_residents": "tract_reports_per_1k_pop",
        "reports_per_sqkm": "tract_reports_per_sqkm",
        "pct_phone": "tract_pct_phone",
        "pct_digital": "tract_pct_digital",
        "pop2020": "tract_pop2020",
    }, inplace=True)

    # Density tier
    def density_tier(r: float) -> str:
        if pd.isna(r):
            return "Unknown"
        if r >= 5000:
            return "EXTREME (≥5000/1k)"
        if r >= 2000:
            return "VERY HIGH (≥2000/1k)"
        if r >= 1000:
            return "HIGH (≥1000/1k)"
        if r >= 500:
            return "MODERATE (≥500/1k)"
        return "LOW (<500/1k)"

    stops["tract_density_tier"] = stops["tract_reports_per_1k_pop"].apply(density_tier)

    # Digital access category: high digital = above citywide average (35.8%)
    stops["tract_digital_access"] = stops["tract_pct_digital"].apply(
        lambda x: "HIGH DIGITAL" if x >= 50 else ("LOW DIGITAL" if x < 30 else "MODERATE DIGITAL")
        if not pd.isna(x) else "Unknown"
    )

    return stops


# ─────────────────────────────────────────────────────────────────────────────
# 2.  Enrich gap analysis
# ─────────────────────────────────────────────────────────────────────────────
def enrich_gap(linkage: pd.DataFrame) -> pd.DataFrame:
    gap = pd.read_csv(GAP_BY_STOP)
    enrich_cols = ["stop_id", "geoid", "tract_name", "tract_total_311_reports",
                   "tract_reports_per_1k_pop", "tract_reports_per_sqkm",
                   "tract_pct_phone", "tract_pct_digital", "tract_pop2020",
                   "tract_density_tier", "tract_digital_access"]
    enriched = gap.merge(linkage[enrich_cols], on="stop_id", how="left")
    return enriched


# ─────────────────────────────────────────────────────────────────────────────
# 3.  Equity tract density summary by district
# ─────────────────────────────────────────────────────────────────────────────
def build_equity_tract_summary(linkage: pd.DataFrame) -> pd.DataFrame:
    gap = pd.read_csv(GAP_BY_STOP)[["stop_id", "council_district", "gap_index_100", "gap_priority"]]
    merged = linkage.merge(gap, on="stop_id", how="left")

    grp = merged.groupby("council_district").agg(
        stops_in_district=("stop_id", "count"),
        mean_tract_density_per_1k=("tract_reports_per_1k_pop", "mean"),
        max_tract_density_per_1k=("tract_reports_per_1k_pop", "max"),
        mean_tract_pct_phone=("tract_pct_phone", "mean"),
        mean_tract_pct_digital=("tract_pct_digital", "mean"),
        mean_gap_index=("gap_index_100", "mean"),
        severe_gap_stops=("gap_priority", lambda x: (x == "SEVERE GAP").sum()),
    ).round(1).reset_index()

    # Phone dependency flag: above 65% phone = high phone dependency
    grp["phone_dependency"] = grp["mean_tract_pct_phone"].apply(
        lambda x: "HIGH" if x >= 65 else ("MODERATE" if x >= 50 else "LOW")
    )
    return grp.sort_values("mean_gap_index", ascending=False)


# ─────────────────────────────────────────────────────────────────────────────
# 4.  Figures
# ─────────────────────────────────────────────────────────────────────────────
def fig_scatter(enriched_gap: pd.DataFrame) -> None:
    """Gap index vs tract density scatter — one point per stop."""
    df = enriched_gap.dropna(subset=["tract_reports_per_1k_pop", "gap_index_100"])
    # Cap outlier tract (pop=3) for display
    df = df[df["tract_reports_per_1k_pop"] < 20000]

    colors = [gap_tier_color(t) for t in df["gap_priority"]]
    sizes = [max(40, t / 30) for t in df["trip_count"]]

    fig, ax = plt.subplots(figsize=(12, 8), facecolor=BG)
    ax.set_facecolor(BG)

    scatter = ax.scatter(
        df["tract_reports_per_1k_pop"],
        df["gap_index_100"],
        c=colors, s=sizes, alpha=0.85, edgecolors="white", linewidth=0.5,
    )

    # Label each stop
    for _, row in df.iterrows():
        label = row["stop_name"].replace("Station", "Stn").replace("Street", "St")[:28]
        ax.annotate(label, (row["tract_reports_per_1k_pop"], row["gap_index_100"]),
                    fontsize=7, color=SLATE,
                    xytext=(6, 2), textcoords="offset points")

    # Reference lines
    ax.axhline(25, color=DARK_RED, linestyle="--", alpha=0.5, linewidth=1.2, label="SEVERE GAP threshold (25)")
    ax.axvline(2000, color=ORANGE, linestyle="--", alpha=0.5, linewidth=1.2, label="Very High Density threshold (2000/1k)")

    # Legend for tiers
    from matplotlib.patches import Patch
    legend_els = [
        Patch(facecolor=DARK_RED, label="SEVERE GAP"),
        Patch(facecolor=RED, label="HIGH GAP"),
        Patch(facecolor=ORANGE, label="MODERATE GAP"),
        Patch(facecolor=GREEN, label="LOWER GAP"),
    ]
    ax.legend(handles=legend_els, fontsize=9, loc="lower right",
              title="Gap Priority Tier", title_fontsize=9)

    ax.set_xlabel("Tract 311 Density (Reports per 1,000 Residents)", color=SLATE, fontsize=11)
    ax.set_ylabel("Supply-Demand Gap Index", color=SLATE, fontsize=11)
    ax.set_title(
        "311 Report Density vs. Infrastructure Gap by Stop\nHigher = more under-served relative to demand",
        fontsize=13, fontweight="bold", color=NAVY,
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.25, color=SLATE)
    ax.tick_params(colors=SLATE)

    # Size legend note
    ax.text(0.01, 0.99, "Circle size ∝ weekly trips", transform=ax.transAxes,
            fontsize=8, color=SLATE, va="top")

    fig.text(0.5, 0.01,
             "Source: Austin 311 (Oct 2021–Apr 2026), CapMetro GTFS, gap analysis pipeline.",
             ha="center", fontsize=7, color=SLATE)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    out = OUT_FIGS / "stop_tract_density_scatter.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


def fig_combined(enriched_gap: pd.DataFrame, equity_summary: pd.DataFrame) -> None:
    """4-panel: (1) tract density by stop, (2) gap index by stop,
    (3) phone vs digital by district, (4) density + gap by district."""

    df = enriched_gap.dropna(subset=["tract_reports_per_1k_pop"]).copy()
    # Remove statistical outlier
    df = df[df["tract_reports_per_1k_pop"] < 20000]
    df = df.sort_values("tract_reports_per_1k_pop", ascending=False).head(20)

    fig = plt.figure(figsize=(20, 16), facecolor=BG)
    fig.suptitle(
        "311 Density, Digital Divide & Infrastructure Gap — High-Demand Stops and Districts",
        fontsize=15, fontweight="bold", color=NAVY, y=0.99,
    )

    # ── Panel 1: tract density per stop ──────────────────────────────────────
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.set_facecolor(BG)
    labels1 = df["stop_name"].str.replace("Station", "Stn").str.replace("Street", "St").str[:30]
    colors1 = [
        DARK_RED if r >= 5000 else RED if r >= 2000 else ORANGE if r >= 1000 else GREEN
        for r in df["tract_reports_per_1k_pop"]
    ]
    bars1 = ax1.barh(labels1[::-1], df["tract_reports_per_1k_pop"][::-1],
                     color=colors1[::-1], edgecolor="white")
    ax1.set_xlabel("Tract 311 Reports / 1,000 Residents", color=SLATE, fontsize=9)
    ax1.set_title("Tract 311 Density at Stop Location", color=NAVY, fontsize=11, fontweight="bold")
    ax1.spines[["top", "right", "left"]].set_visible(False)
    ax1.grid(axis="x", alpha=0.3, color=SLATE)
    ax1.tick_params(axis="y", labelsize=7.5, colors=SLATE)
    ax1.tick_params(axis="x", colors=SLATE)
    for bar, val in zip(bars1[::-1], df["tract_reports_per_1k_pop"]):
        ax1.text(bar.get_width() + 30, bar.get_y() + bar.get_height() / 2,
                 f"{val:,.0f}", va="center", ha="left", fontsize=7, color=SLATE)

    # ── Panel 2: gap index per stop ───────────────────────────────────────────
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.set_facecolor(BG)
    df_gap = enriched_gap.sort_values("gap_index_100", ascending=False).head(20)
    labels2 = df_gap["stop_name"].str.replace("Station", "Stn").str.replace("Street", "St").str[:30]
    colors2 = [gap_tier_color(t) for t in df_gap["gap_priority"]]
    bars2 = ax2.barh(labels2[::-1], df_gap["gap_index_100"][::-1],
                     color=colors2[::-1], edgecolor="white")
    ax2.axvline(25, color=DARK_RED, linestyle="--", alpha=0.5, linewidth=1, label="SEVERE threshold")
    ax2.set_xlabel("Supply-Demand Gap Index (0–100)", color=SLATE, fontsize=9)
    ax2.set_title("Infrastructure Gap Index by Stop", color=NAVY, fontsize=11, fontweight="bold")
    ax2.spines[["top", "right", "left"]].set_visible(False)
    ax2.grid(axis="x", alpha=0.3, color=SLATE)
    ax2.tick_params(axis="y", labelsize=7.5, colors=SLATE)
    ax2.tick_params(axis="x", colors=SLATE)
    ax2.legend(fontsize=8, loc="lower right")
    for bar, val in zip(bars2[::-1], df_gap["gap_index_100"]):
        ax2.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                 f"{val:.1f}", va="center", ha="left", fontsize=7, color=SLATE)

    # ── Panel 3: phone vs digital by district ─────────────────────────────────
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.set_facecolor(BG)
    eq = equity_summary[equity_summary["council_district"] > 0].sort_values("council_district")
    x = np.arange(len(eq))
    width = 0.55
    phone_vals = eq["mean_tract_pct_phone"].values
    digital_vals = eq["mean_tract_pct_digital"].values
    other_vals = np.clip(100 - phone_vals - digital_vals, 0, 100)
    ax3.bar(x, phone_vals, width, label="Phone", color=NAVY)
    ax3.bar(x, digital_vals, width, bottom=phone_vals, label="Digital (App/Web)", color=GREEN)
    ax3.bar(x, other_vals, width, bottom=phone_vals + digital_vals, label="Other", color=SLATE, alpha=0.4)
    ax3.set_xticks(x)
    ax3.set_xticklabels([f"D{int(d)}" for d in eq["council_district"]], fontsize=9, color=SLATE)
    ax3.set_ylabel("Mean % of Tract 311 Reports", color=SLATE, fontsize=9)
    ax3.set_ylim(0, 105)
    ax3.set_title("Digital Divide at Stop Tract Level by District", color=NAVY, fontsize=11, fontweight="bold")
    ax3.spines[["top", "right"]].set_visible(False)
    ax3.grid(axis="y", alpha=0.3, color=SLATE)
    ax3.legend(fontsize=8, loc="upper right")
    ax3.tick_params(axis="y", colors=SLATE)
    for xi, (pp, dp) in enumerate(zip(phone_vals, digital_vals)):
        ax3.text(xi, pp / 2, f"{pp:.0f}%", ha="center", va="center",
                 fontsize=8, color="white", fontweight="bold")
        if dp > 5:
            ax3.text(xi, pp + dp / 2, f"{dp:.0f}%", ha="center", va="center",
                     fontsize=8, color="white", fontweight="bold")

    # ── Panel 4: density + gap by district (dual axis) ───────────────────────
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.set_facecolor(BG)
    eq_s = equity_summary[equity_summary["council_district"] > 0].sort_values("council_district")
    x4 = np.arange(len(eq_s))
    width4 = 0.35
    bars_d = ax4.bar(x4 - width4/2, eq_s["mean_tract_density_per_1k"], width4,
                     label="Mean Tract Density (reports/1k)", color=NAVY, alpha=0.85)
    ax4b = ax4.twinx()
    ax4b.set_facecolor(BG)
    bars_g = ax4b.bar(x4 + width4/2, eq_s["mean_gap_index"], width4,
                      label="Mean Gap Index", color=RED, alpha=0.85)
    ax4.set_xticks(x4)
    ax4.set_xticklabels([f"D{int(d)}" for d in eq_s["council_district"]], fontsize=9, color=SLATE)
    ax4.set_ylabel("Mean Tract 311 Density (reports/1k pop)", color=NAVY, fontsize=9)
    ax4b.set_ylabel("Mean Supply-Demand Gap Index", color=RED, fontsize=9)
    ax4.set_title("Tract 311 Density vs. Gap Index by District", color=NAVY, fontsize=11, fontweight="bold")
    ax4.spines[["top"]].set_visible(False)
    ax4b.spines[["top"]].set_visible(False)
    ax4.tick_params(axis="y", colors=NAVY)
    ax4b.tick_params(axis="y", colors=RED)
    ax4.tick_params(axis="x", colors=SLATE)
    lines1, labels1_ = ax4.get_legend_handles_labels()
    lines2, labels2_ = ax4b.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1_ + labels2_, fontsize=8, loc="upper left")

    fig.text(0.5, 0.005,
             "Source: Austin 311 Service Requests (Oct 2021–Apr 2026), CapMetro GTFS, gap analysis pipeline. "
             "Travis County census tracts. 2020 Census population.",
             ha="center", fontsize=7, color=SLATE)
    plt.tight_layout(rect=[0, 0.025, 1, 0.98])
    out = OUT_FIGS / "stop_tract_density_combined.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


def fig_simple_density(enriched_gap: pd.DataFrame) -> None:
    """Simple slide-friendly chart: tract density by stop with severe-gap highlight."""
    df = enriched_gap.dropna(subset=["tract_reports_per_1k_pop"]).copy()
    df = df[df["tract_reports_per_1k_pop"] < 20000]
    df = df.sort_values("tract_reports_per_1k_pop", ascending=True)

    fig, ax = plt.subplots(figsize=(13, 10), facecolor=BG)
    ax.set_facecolor(BG)

    labels = (
        df["stop_name"]
        .str.replace("Station", "Stn", regex=False)
        .str.replace("Street", "St", regex=False)
        .str[:34]
    )

    # Keep color logic simple for readability in rooms and printouts.
    colors = np.where(df["gap_priority"] == "SEVERE GAP", DARK_RED, NAVY)
    bars = ax.barh(labels, df["tract_reports_per_1k_pop"], color=colors, edgecolor="white")

    ax.axvline(2000, color=ORANGE, linestyle="--", linewidth=1.5, alpha=0.9)
    ax.text(
        2000,
        0.5,
        "  Very high density threshold (2,000/1k)",
        transform=ax.get_xaxis_transform(),
        color=ORANGE,
        fontsize=9,
        va="center",
    )

    ax.set_title(
        "311 Complaint Density at Each High-Demand Stop's Tract",
        fontsize=14,
        fontweight="bold",
        color=NAVY,
    )
    ax.set_xlabel("Reports per 1,000 residents (Oct 2021-Apr 2026)", color=SLATE, fontsize=11)
    ax.set_ylabel("High-demand stops", color=SLATE, fontsize=11)
    ax.grid(axis="x", alpha=0.25, color=SLATE)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=8, colors=SLATE)
    ax.tick_params(axis="x", colors=SLATE)
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

    # Label only high-end bars to reduce clutter.
    for bar, val in zip(bars, df["tract_reports_per_1k_pop"]):
        if val >= 3000:
            ax.text(
                bar.get_width() + 45,
                bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f}",
                va="center",
                fontsize=8,
                color=SLATE,
            )

    from matplotlib.patches import Patch
    legend_els = [
        Patch(facecolor=DARK_RED, label="SEVERE GAP stop"),
        Patch(facecolor=NAVY, label="Other high-demand stop"),
    ]
    ax.legend(handles=legend_els, fontsize=9, loc="lower right", frameon=False)

    fig.text(
        0.5,
        0.01,
        "Source: Austin 311, stop-level gap analysis, Travis County tract assignment.",
        ha="center",
        fontsize=8,
        color=SLATE,
    )
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    out = OUT_FIGS / "stop_tract_density_simple.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    print("Building stop → tract → density linkage…")
    linkage = build_linkage()
    print(f"  Stops linked: {len(linkage)}")

    print("Enriching gap analysis…")
    enriched_gap = enrich_gap(linkage)

    print("Building equity tract density summary by district…")
    equity_summary = build_equity_tract_summary(linkage)

    # ── save tables ────────────────────────────────────────────────────────────
    linkage_out = OUT_TABLES / "stop_tract_density_linkage.csv"
    gap_enriched_out = OUT_TABLES / "gap_analysis_with_tract_density.csv"
    equity_out = OUT_TABLES / "equity_tract_density_summary.csv"

    linkage.to_csv(linkage_out, index=False)
    enriched_gap.to_csv(gap_enriched_out, index=False)
    equity_summary.to_csv(equity_out, index=False)
    print(f"Saved {linkage_out}")
    print(f"Saved {gap_enriched_out}")
    print(f"Saved {equity_out}")

    # ── summary ────────────────────────────────────────────────────────────────
    print("\n=== STOP → TRACT DENSITY LINKAGE ===")
    for _, r in linkage.sort_values("tract_reports_per_1k_pop", ascending=False).head(15).iterrows():
        print(f"  {r['stop_name'][:38]:38s} → {r['tract_name']:22s} "
              f"  {r['tract_reports_per_1k_pop']:>8,.0f}/1k  "
              f"  {r['tract_pct_digital']:.0f}% digital  [{r['tract_density_tier']}]")

    print("\n=== EQUITY DISTRICT SUMMARY (density + gap) ===")
    for _, r in equity_summary.iterrows():
        print(f"  District {int(r['council_district'])}: "
              f"density={r['mean_tract_density_per_1k']:.0f}/1k  "
              f"gap={r['mean_gap_index']:.1f}  "
              f"phone={r['mean_tract_pct_phone']:.0f}%  "
              f"severe_gaps={int(r['severe_gap_stops'])}  "
              f"phone_dep={r['phone_dependency']}")

    # ── figures ────────────────────────────────────────────────────────────────
    print("\nGenerating figures…")
    fig_scatter(enriched_gap)
    fig_combined(enriched_gap, equity_summary)
    fig_simple_density(enriched_gap)
    print("Done.")


if __name__ == "__main__":
    main()
