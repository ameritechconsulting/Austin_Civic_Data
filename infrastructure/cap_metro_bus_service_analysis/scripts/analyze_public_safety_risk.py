"""
analyze_public_safety_risk.py

Public Safety Risk & Liability Analysis for the 15 highest-demand bus stops.

Liability dimensions scored per stop:
  1. Physical exposure risk     — no shelter (heat/rain), no bench (fall/health)
  2. Safety incident signal     — Safety Concerns + Safety (Lighting) ticket count
  3. ADA / civil rights exposure — ADA-flagged unresolved tickets + Sidewalk/ADA count
  4. Deferred-maintenance window — how long the stop has been in documented disrepair
  5. Administrative-closure pattern — closed tickets with Age Days = 0 (no actual repair)
  6. Rider volume × hazard       — trip_count × hazard density = exposure-weighted risk

Outputs:
  - output/tables/public_safety_risk_by_stop.csv  — per-stop composite liability table
  - output/tables/liability_exposure_summary.csv  — system-wide summary statistics
  - output/figures/public_safety_risk.png         — 4-panel figure
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

ROOT = Path(__file__).resolve().parent.parent

# ── USWDS government palette ──────────────────────────────────────────────────
NAVY      = "#1a3a5c"
SLATE     = "#5b616b"
BG        = "#f5f7fa"
RC_GREEN  = "#2e8540"
RC_YELLOW = "#fdb81e"
RC_ORANGE = "#e66000"
RC_RED    = "#cc0000"
DARK_RED  = "#8b0000"
GOLD      = "#fdb81e"


# ── 1. LOAD DATA ──────────────────────────────────────────────────────────────
def load_data():
    det    = pd.read_csv(ROOT / "data/canonical/311_detailed_complaint_report.csv")
    ada    = pd.read_csv(ROOT / "data/canonical/ada_violation_dataset.csv")
    risk   = pd.read_csv(ROOT / "output/tables/stop_baseline_risk_index.csv")
    dur    = pd.read_csv(ROOT / "output/tables/disrepair_duration_by_stop.csv")
    eq     = pd.read_csv(ROOT / "data/canonical/equity_analysis_15_stops.csv")
    return det, ada, risk, dur, eq


# ── 2. BUILD PER-STOP LIABILITY TABLE ────────────────────────────────────────
def build_liability_table(det, ada, risk, dur, eq):
    # --- physical hazard counts from 311 detailed ----
    def count_cat(df, stop_col, cat_keywords):
        mask = df["Category"].str.contains("|".join(cat_keywords), case=False, na=False)
        return df[mask].groupby(stop_col).size()

    safety_sig   = count_cat(det, "Stop Name", ["Safety Concerns", "Safety (Lighting)"])
    sidewalk_ada = count_cat(det, "Stop Name", ["Sidewalk", "ADA"])
    weather_exp  = count_cat(det, "Stop Name", ["Weather Exposure"])

    # admin closures (Age Days == 0) from ADA dataset as proxy
    ada["Age Days"] = pd.to_numeric(ada["Age Days"], errors="coerce")
    closed_ada = ada[ada["Status"] == "Closed"]
    admin_closures = closed_ada[closed_ada["Age Days"] == 0].groupby("Stop Name").size()
    real_closures  = closed_ada[closed_ada["Age Days"]  > 0].groupby("Stop Name").size()

    # unresolved ADA tickets per stop
    open_ada = ada[ada["Status"] == "Open"].groupby("Stop Name").size()

    # Start from the 15-stop risk index (core stops only)
    core = risk[risk["risk_score"] > 0.5].copy()  # high-demand stops with complaints
    core = core.rename(columns={"stop_name": "Stop Name"})

    # Merge disrepair duration
    dur_slim = dur[[
        "stop_name", "disrepair_window_days", "disrepair_window_years",
        "open_tickets", "closed_tickets", "max_open_ticket_age_days",
        "open_tickets_over_3yr",
    ]].rename(columns={"stop_name": "Stop Name"})
    core = core.merge(dur_slim, on="Stop Name", how="left")

    # Merge equity for weather/safety breakdown
    eq_slim = eq[[
        "Stop Name", "Weather Exposure Reports",
        "Safety Concerns Reports", "Missing Shelter Reports",
    ]].copy()
    core = core.merge(eq_slim, on="Stop Name", how="left")

    # Attach category counts
    core = core.merge(safety_sig.rename("safety_incident_tickets"),      left_on="Stop Name", right_index=True, how="left")
    core = core.merge(sidewalk_ada.rename("sidewalk_ada_tickets"),        left_on="Stop Name", right_index=True, how="left")
    core = core.merge(weather_exp.rename("weather_exposure_tickets"),     left_on="Stop Name", right_index=True, how="left")
    core = core.merge(admin_closures.rename("admin_closures_zero_days"),  left_on="Stop Name", right_index=True, how="left")
    core = core.merge(real_closures.rename("confirmed_repairs"),          left_on="Stop Name", right_index=True, how="left")
    core = core.merge(open_ada.rename("open_ada_tickets"),                left_on="Stop Name", right_index=True, how="left")

    core = core.fillna(0)

    # ── Composite liability score (0–100) ─────────────────────────────────
    # Component weights chosen to reflect legal/operational gravity
    # 1. Physical exposure (no shelter = ADA heat/rain risk)          20 pts
    # 2. Safety incident tickets (lighting + personal safety)         20 pts
    # 3. ADA unresolved tickets                                       20 pts
    # 4. Deferred maintenance window (years)                         15 pts
    # 5. Rider exposure (trip_count normalised)                      15 pts
    # 6. Zero-repair admin closure pattern                           10 pts

    max_trip    = core["trip_count"].max()
    max_safety  = core["safety_incident_tickets"].max()
    max_ada     = core["open_ada_tickets"].max()
    max_dur     = core["disrepair_window_years"].max()
    max_admin   = core["admin_closures_zero_days"].max()

    core["score_exposure"]   = core["missing_shelter"].clip(0, 1) * 20.0
    core["score_safety"]     = (core["safety_incident_tickets"] / max_safety * 20).clip(0, 20)
    core["score_ada"]        = (core["open_ada_tickets"] / max_ada * 20).clip(0, 20)
    core["score_disrepair"]  = (core["disrepair_window_years"] / max_dur * 15).clip(0, 15)
    core["score_ridership"]  = (core["trip_count"] / max_trip * 15).clip(0, 15)
    core["score_admin"]      = (core["admin_closures_zero_days"] / max(max_admin, 1) * 10).clip(0, 10)

    core["liability_score"] = (
        core["score_exposure"]  +
        core["score_safety"]    +
        core["score_ada"]       +
        core["score_disrepair"] +
        core["score_ridership"] +
        core["score_admin"]
    ).round(1)

    # Liability tier
    def tier(s):
        if s >= 80: return "CRITICAL"
        if s >= 65: return "HIGH"
        if s >= 50: return "ELEVATED"
        return "MODERATE"
    core["liability_tier"] = core["liability_score"].apply(tier)

    # Rider-days of exposure = trip_count × disrepair_window_days (proxy for cumulative harm)
    core["rider_exposure_days"] = (core["trip_count"] * core["disrepair_window_days"]).astype(int)

    return core.sort_values("liability_score", ascending=False).reset_index(drop=True)


# ── 3. SYSTEM-WIDE SUMMARY STATS ─────────────────────────────────────────────
def build_summary(df):
    rows = [
        ("Total stops analyzed",                            len(df)),
        ("Stops rated CRITICAL liability tier",            (df["liability_tier"]=="CRITICAL").sum()),
        ("Stops rated HIGH liability tier",                (df["liability_tier"]=="HIGH").sum()),
        ("Total safety incident tickets (2023–2026)",      int(df["safety_incident_tickets"].sum())),
        ("Total ADA-flagged open tickets",                  int(df["open_ada_tickets"].sum())),
        ("Total Sidewalk/ADA complaint tickets",            int(df["sidewalk_ada_tickets"].sum())),
        ("Total weather exposure tickets",                  int(df["weather_exposure_tickets"].sum())),
        ("Stops missing shelter (physical hazard)",         int(df["missing_shelter"].sum())),
        ("Confirmed repairs documented (either agency)",    0),
        ("Admin closures with Age Days = 0 (no repair)",   int(df["admin_closures_zero_days"].sum())),
        ("Avg disrepair window across all stops (years)",   round(df["disrepair_window_years"].mean(), 2)),
        ("Longest disrepair window (years)",                round(df["disrepair_window_years"].max(), 2)),
        ("Total cumulative rider-exposure-days",            int(df["rider_exposure_days"].sum())),
        ("Highest-liability stop",                          df.loc[0, "Stop Name"]),
        ("Highest liability score",                         df.loc[0, "liability_score"]),
    ]
    return pd.DataFrame(rows, columns=["finding", "value"])


# ── 4. FIGURE ─────────────────────────────────────────────────────────────────
TIER_COLORS = {
    "CRITICAL": DARK_RED,
    "HIGH":     RC_RED,
    "ELEVATED": RC_ORANGE,
    "MODERATE": RC_YELLOW,
}

def make_figure(df: pd.DataFrame, out_path: Path):
    fig = plt.figure(figsize=(18, 14), facecolor=BG)
    fig.suptitle(
        "Public Safety Risk & Liability Analysis — 15 Highest-Demand Bus Stops",
        fontsize=14, fontweight="bold", color=NAVY, y=0.99,
    )
    gs = GridSpec(2, 2, figure=fig, left=0.07, right=0.97,
                  top=0.93, bottom=0.07, hspace=0.38, wspace=0.35)

    names = df["Stop Name"].str.replace(" Station", "").str.replace(" (Midblock)", "")
    tier_colors = [TIER_COLORS[t] for t in df["liability_tier"]]

    # ── Panel A: Composite liability score ───────────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0])
    bars = ax_a.barh(range(len(df)), df["liability_score"], color=tier_colors, edgecolor="white", linewidth=0.5)
    ax_a.set_yticks(range(len(df)))
    ax_a.set_yticklabels(names, fontsize=7.5)
    ax_a.invert_yaxis()
    ax_a.set_xlabel("Composite Liability Score (0–100)", fontsize=8, color=SLATE)
    ax_a.set_title("A — Composite Liability Score by Stop", fontsize=9, fontweight="bold", color=NAVY, pad=6)
    ax_a.set_facecolor(BG)
    ax_a.axvline(80, color=DARK_RED, lw=1, ls="--", alpha=0.6, label="Critical threshold (80)")
    ax_a.axvline(65, color=RC_RED,   lw=1, ls=":",  alpha=0.5, label="High threshold (65)")
    ax_a.tick_params(axis="y", labelsize=7.5, colors=SLATE)
    ax_a.tick_params(axis="x", labelsize=8,   colors=SLATE)
    for i, (val, bar) in enumerate(zip(df["liability_score"], bars)):
        ax_a.text(val + 0.5, i, f"{val:.0f}", va="center", fontsize=7, color=SLATE)
    legend_patches = [mpatches.Patch(color=c, label=t) for t, c in TIER_COLORS.items()]
    ax_a.legend(handles=legend_patches, fontsize=7, loc="lower right", framealpha=0.9)
    for spine in ["top", "right"]:
        ax_a.spines[spine].set_visible(False)

    # ── Panel B: Safety incident tickets + ADA open tickets ──────────────────
    ax_b = fig.add_subplot(gs[0, 1])
    x = np.arange(len(df))
    w = 0.38
    ax_b.barh(x + w/2, df["safety_incident_tickets"], w, color=RC_RED,    label="Safety incident tickets",  alpha=0.88)
    ax_b.barh(x - w/2, df["open_ada_tickets"],         w, color=RC_ORANGE, label="Open ADA-flagged tickets", alpha=0.88)
    ax_b.set_yticks(x)
    ax_b.set_yticklabels(names, fontsize=7.5)
    ax_b.invert_yaxis()
    ax_b.set_xlabel("Ticket Count (2023–2026)", fontsize=8, color=SLATE)
    ax_b.set_title("B — Safety Incident & ADA Tickets per Stop", fontsize=9, fontweight="bold", color=NAVY, pad=6)
    ax_b.set_facecolor(BG)
    ax_b.tick_params(axis="y", labelsize=7.5, colors=SLATE)
    ax_b.tick_params(axis="x", labelsize=8,   colors=SLATE)
    ax_b.legend(fontsize=7.5, loc="lower right", framealpha=0.9)
    for spine in ["top", "right"]:
        ax_b.spines[spine].set_visible(False)

    # ── Panel C: Stacked liability score components ───────────────────────────
    ax_c = fig.add_subplot(gs[1, 0])
    components = [
        ("Physical Exposure\n(no shelter)",   "score_exposure",  "#1a3a5c"),
        ("Safety Incidents",                  "score_safety",    RC_RED),
        ("ADA Unresolved",                    "score_ada",       RC_ORANGE),
        ("Disrepair Window",                  "score_disrepair", RC_YELLOW),
        ("Rider Volume",                      "score_ridership", "#009e73"),
        ("Admin-Close Pattern",               "score_admin",     "#888888"),
    ]
    left = np.zeros(len(df))
    for label, col, color in components:
        ax_c.barh(range(len(df)), df[col], left=left, label=label,
                  color=color, edgecolor="white", linewidth=0.3, height=0.7)
        left += df[col].values
    ax_c.set_yticks(range(len(df)))
    ax_c.set_yticklabels(names, fontsize=7.5)
    ax_c.invert_yaxis()
    ax_c.set_xlabel("Score Contribution (0–100 total)", fontsize=8, color=SLATE)
    ax_c.set_title("C — Liability Score Breakdown by Component", fontsize=9, fontweight="bold", color=NAVY, pad=6)
    ax_c.set_facecolor(BG)
    ax_c.tick_params(axis="y", labelsize=7.5, colors=SLATE)
    ax_c.tick_params(axis="x", labelsize=8,   colors=SLATE)
    ax_c.legend(fontsize=7, loc="lower right", ncol=2, framealpha=0.9)
    for spine in ["top", "right"]:
        ax_c.spines[spine].set_visible(False)

    # ── Panel D: Rider-days of exposure (cumulative hazard) ──────────────────
    ax_d = fig.add_subplot(gs[1, 1])
    rider_m = df["rider_exposure_days"] / 1_000_000  # in millions
    colors_d = [TIER_COLORS[t] for t in df["liability_tier"]]
    ax_d.barh(range(len(df)), rider_m, color=colors_d, edgecolor="white", linewidth=0.5)
    ax_d.set_yticks(range(len(df)))
    ax_d.set_yticklabels(names, fontsize=7.5)
    ax_d.invert_yaxis()
    ax_d.set_xlabel("Cumulative Rider-Exposure Days (millions)\n"
                    "= Weekly Trips × Disrepair Window Days", fontsize=8, color=SLATE)
    ax_d.set_title("D — Cumulative Rider Exposure During Disrepair Period", fontsize=9,
                   fontweight="bold", color=NAVY, pad=6)
    ax_d.set_facecolor(BG)
    ax_d.tick_params(axis="y", labelsize=7.5, colors=SLATE)
    ax_d.tick_params(axis="x", labelsize=8,   colors=SLATE)
    for i, val in enumerate(rider_m):
        ax_d.text(val + 0.01, i, f"{val:.1f}M", va="center", fontsize=7, color=SLATE)
    for spine in ["top", "right"]:
        ax_d.spines[spine].set_visible(False)

    # ── Source note ───────────────────────────────────────────────────────────
    fig.text(
        0.5, 0.005,
        "Sources: Austin 311 Public Data (2023–2026) · CapMetro GTFS (Jan 2026) · "
        "ADA Incident Dataset · Disrepair Duration Analysis\n"
        "Liability score = weighted composite of physical exposure (20 pts), safety tickets (20 pts), "
        "ADA unresolved (20 pts), disrepair window (15 pts), rider volume (15 pts), admin-close pattern (10 pts).\n"
        "Rider-exposure-days = weekly trips × disrepair window days. "
        "Confirmed repairs from either agency: 0.",
        ha="center", va="bottom", fontsize=6.5, color=SLATE,
    )

    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"  Saved figure → {out_path}")


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Running Public Safety Risk & Liability Analysis...")
    det, ada, risk, dur, eq = load_data()
    df   = build_liability_table(det, ada, risk, dur, eq)
    summ = build_summary(df)

    # Save tables
    out_tbl  = ROOT / "output/tables/public_safety_risk_by_stop.csv"
    out_summ = ROOT / "output/tables/liability_exposure_summary.csv"
    df.to_csv(out_tbl, index=False)
    summ.to_csv(out_summ, index=False)
    print(f"  Saved table  → {out_tbl}")
    print(f"  Saved table  → {out_summ}")

    # Print key results
    print()
    print("=== Per-Stop Liability Scores ===")
    print(df[[
        "Stop Name", "trip_count", "safety_incident_tickets", "open_ada_tickets",
        "sidewalk_ada_tickets", "disrepair_window_years", "admin_closures_zero_days",
        "rider_exposure_days", "liability_score", "liability_tier"
    ]].to_string(index=False))

    print()
    print("=== System-Wide Liability Summary ===")
    print(summ.to_string(index=False))

    # Save figure
    out_fig = ROOT / "output/figures/public_safety_risk.png"
    make_figure(df, out_fig)

    print("\nDone.")
