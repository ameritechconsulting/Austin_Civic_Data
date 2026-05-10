"""
build_district_report_card.py

Produces a council-district report card combining:
  - Census demographics (population, race/ethnicity) from 2020 redistricting data
  - Amenity gap (missing shelter/bench) at high-priority stops per district
  - Transit problem scores (open tickets, response rates, ticket age)

Outputs:
  - output/tables/district_report_card.csv
  - output/figures/district_report_card.png
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import to_rgba

ROOT = Path(__file__).resolve().parent.parent

# ── USWDS government palette ──────────────────────────────────────────────────
NAVY   = "#1a3a5c"
SLATE  = "#5b616b"
BG     = "#f5f7fa"
RC_GREEN  = "#2e8540"
RC_YELLOW = "#fdb81e"
RC_ORANGE = "#e66000"
RC_RED    = "#cc0000"
DARK_RED  = "#8b0000"


# ── 1. DEMOGRAPHICS — aggregate tract-level data to district ─────────────────
def load_demographics():
    crosswalk = pd.read_csv(ROOT / "data/reference/austin_tracts_by_council_district.csv")
    # Normalize crosswalk geoid to 11-digit string for join
    crosswalk["geoid11"] = crosswalk["geoid"].astype(str).str.strip()

    redist = pd.read_csv(
        ROOT / "archive/sources/austin_msa_5_county_tract_redistricting_2020_2026_04_17.csv",
        usecols=["GEOID", "GEOCODE", "POP100",
                 "P0010001",  # total population
                 "P0010003",  # White alone
                 "P0010004",  # Black or African American alone
                 "P0010006",  # Asian alone
                 "P0020002",  # Hispanic or Latino (any race)
                 "P0020005",  # Non-Hispanic White alone
                 "P0020006",  # Non-Hispanic Black alone
                 ],
        dtype=str,
    )

    # Build a clean 11-digit GEOID from GEOCODE (already 11 chars like "48453001234")
    redist["geoid11"] = redist["GEOCODE"].astype(str).str.strip()

    # Coerce numeric columns
    num_cols = ["P0010001", "P0010003", "P0010004", "P0010006",
                "P0020002", "P0020005", "P0020006"]
    for c in num_cols:
        redist[c] = pd.to_numeric(redist[c].str.replace(",", ""), errors="coerce").fillna(0)

    # Join
    merged = crosswalk.merge(redist[["geoid11"] + num_cols], on="geoid11", how="left")

    # Aggregate to district
    demo = merged.groupby("council_district")[num_cols].sum().reset_index()
    demo.rename(columns={
        "P0010001": "total_pop",
        "P0010003": "white_alone",
        "P0010004": "black_alone",
        "P0010006": "asian_alone",
        "P0020002": "hispanic",
        "P0020005": "nh_white",
        "P0020006": "nh_black",
    }, inplace=True)

    demo["pct_nonwhite"]  = ((demo["total_pop"] - demo["nh_white"]) / demo["total_pop"] * 100).round(1)
    demo["pct_hispanic"]  = (demo["hispanic"] / demo["total_pop"] * 100).round(1)
    demo["pct_black"]     = (demo["nh_black"] / demo["total_pop"] * 100).round(1)
    demo["pct_asian"]     = (demo["asian_alone"] / demo["total_pop"] * 100).round(1)

    return demo[["council_district", "total_pop", "pct_nonwhite",
                 "pct_hispanic", "pct_black", "pct_asian"]]


# ── 2. TRANSIT METRICS from equity_by_district ───────────────────────────────
def load_transit_metrics():
    df = pd.read_csv(ROOT / "output/tables/equity_by_district.csv")
    df["tickets_per_stop"] = (df["total_open_tickets"] / df["stops"]).round(1)
    return df[[
        "council_district", "stops", "total_open_tickets", "tickets_per_stop",
        "avg_response_rate", "avg_open_ticket_age_days",
        "total_open_over_1yr", "total_open_over_3yr",
        "avg_amenity_gap", "capmetro_pct", "city_pct"
    ]]


# ── 3. GRADING FUNCTIONS ──────────────────────────────────────────────────────
def grade_response_rate(rate):
    """Higher is better — but all districts are failing; scale to show relative harm."""
    if rate >= 50:  return ("A", RC_GREEN)
    if rate >= 35:  return ("B", RC_YELLOW)
    if rate >= 25:  return ("C", RC_ORANGE)
    if rate >= 15:  return ("D", RC_RED)
    return ("F", DARK_RED)

def grade_ticket_age(age):
    """Lower is better."""
    if age < 180:   return ("A", RC_GREEN)
    if age < 365:   return ("B", RC_YELLOW)
    if age < 450:   return ("C", RC_ORANGE)
    if age < 550:   return ("D", RC_RED)
    return ("F", DARK_RED)

def grade_amenity_gap(gap):
    """0 = fully equipped, 2 = missing both."""
    if gap == 0:   return ("A", RC_GREEN)
    if gap <= 0.5: return ("B", RC_YELLOW)
    if gap <= 1.0: return ("C", RC_ORANGE)
    if gap <= 1.5: return ("D", RC_RED)
    return ("F", DARK_RED)

def grade_tickets_per_stop(tps):
    """Lower is better."""
    if tps < 20:   return ("A", RC_GREEN)
    if tps < 40:   return ("B", RC_YELLOW)
    if tps < 60:   return ("C", RC_ORANGE)
    if tps < 80:   return ("D", RC_RED)
    return ("F", DARK_RED)

GRADE_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4}
GRADE_COLORS = {"A": RC_GREEN, "B": RC_YELLOW, "C": RC_ORANGE, "D": RC_RED, "F": DARK_RED}

def overall_grade(grades):
    worst = max(grades, key=lambda g: GRADE_ORDER[g])
    avg_idx = round(np.mean([GRADE_ORDER[g] for g in grades]))
    avg_idx = min(avg_idx, 4)
    letters = ["A", "B", "C", "D", "F"]
    # Blend: if worst is F and avg is D, give F; else give avg
    if GRADE_ORDER[worst] >= 4:
        return "F"
    return letters[avg_idx]


# ── 4. BUILD REPORT CARD TABLE ────────────────────────────────────────────────
def build_report_card(demo, transit):
    rc = transit.merge(demo, on="council_district", how="left")

    rows = []
    for _, r in rc.iterrows():
        g_response  = grade_response_rate(r["avg_response_rate"])[0]
        g_age       = grade_ticket_age(r["avg_open_ticket_age_days"])[0]
        g_amenity   = grade_amenity_gap(r["avg_amenity_gap"])[0]
        g_burden    = grade_tickets_per_stop(r["tickets_per_stop"])[0]
        overall     = overall_grade([g_response, g_age, g_amenity, g_burden])

        rows.append({
            "council_district":        int(r["council_district"]),
            "total_pop":               int(r["total_pop"]),
            "pct_nonwhite":            r["pct_nonwhite"],
            "pct_hispanic":            r["pct_hispanic"],
            "pct_black":               r["pct_black"],
            "pct_asian":               r["pct_asian"],
            "stops_in_analysis":       int(r["stops"]),
            "total_open_tickets":      int(r["total_open_tickets"]),
            "tickets_per_stop":        r["tickets_per_stop"],
            "avg_response_rate_pct":   r["avg_response_rate"],
            "avg_open_ticket_age_days": r["avg_open_ticket_age_days"],
            "tickets_over_1yr":        int(r["total_open_over_1yr"]),
            "tickets_over_3yr":        int(r["total_open_over_3yr"]),
            "avg_amenity_gap":         r["avg_amenity_gap"],
            "capmetro_pct":            r["capmetro_pct"],
            "city_pct":                r["city_pct"],
            "grade_response":          g_response,
            "grade_ticket_age":        g_age,
            "grade_amenity_gap":       g_amenity,
            "grade_burden":            g_burden,
            "grade_overall":           overall,
        })

    df = pd.DataFrame(rows).sort_values("council_district")
    return df


# ── 5. VISUALIZE ──────────────────────────────────────────────────────────────
def make_figure(rc: pd.DataFrame, out_path: Path):
    districts = rc["council_district"].tolist()
    n = len(districts)

    # Metric columns for the heatmap section
    metric_cols = [
        ("Response\nRate", "avg_response_rate_pct",   grade_response_rate,  "{:.0f}%"),
        ("Avg Ticket\nAge (days)", "avg_open_ticket_age_days", grade_ticket_age, "{:.0f}d"),
        ("Amenity\nGap", "avg_amenity_gap",            grade_amenity_gap,    "{:.1f}"),
        ("Tickets /\nStop", "tickets_per_stop",         grade_tickets_per_stop, "{:.0f}"),
    ]

    fig = plt.figure(figsize=(18, max(7, n * 1.5 + 3.0)), facecolor=BG)
    fig.suptitle(
        "Council District Transit Report Card\nDemographics · Amenity Gap · Service Response",
        fontsize=15, fontweight="bold", color=NAVY, y=0.99,
    )

    from matplotlib.gridspec import GridSpec
    # n data rows + 2 header rows
    gs = GridSpec(
        n + 2, 9,
        figure=fig,
        left=0.04, right=0.97,
        top=0.91, bottom=0.09,
        hspace=0.0, wspace=0.2,
        height_ratios=[0.7, 0.7] + [1.0] * n,
    )

    # ── Row 0: section group banners ──────────────────────────────────────────
    DEMO_COLOR   = "#1a3a5c"   # navy
    METRIC_COLOR = "#2c4a6e"   # slightly lighter navy
    GRADE_COLOR  = "#0d2437"   # darker

    for span, color, label in [
        ((0, 4), DEMO_COLOR,   "DEMOGRAPHICS  (2020 Census P.L. 94-171)"),
        ((4, 8), METRIC_COLOR, "TRANSIT SERVICE METRICS  (Austin 311, 2023–2026)"),
        ((8, 9), GRADE_COLOR,  "GRADE"),
    ]:
        ax = fig.add_subplot(gs[0, span[0]:span[1]])
        ax.set_facecolor(color)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.text(0.5, 0.5, label, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color="white")
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

    # ── Row 1: column sub-headers ─────────────────────────────────────────────
    sub_labels_colors = [
        ("District",                          DEMO_COLOR),
        ("Population",                        DEMO_COLOR),
        ("% Non-\nWhite",                     DEMO_COLOR),
        ("Race / Ethnicity\nMix",             DEMO_COLOR),
        (metric_cols[0][0],                   METRIC_COLOR),
        (metric_cols[1][0],                   METRIC_COLOR),
        (metric_cols[2][0],                   METRIC_COLOR),
        (metric_cols[3][0],                   METRIC_COLOR),
        ("Overall\nGrade",                    GRADE_COLOR),
    ]
    for col_idx, (lbl, bg) in enumerate(sub_labels_colors):
        ax = fig.add_subplot(gs[1, col_idx])
        ax.set_facecolor(bg)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.text(0.5, 0.5, lbl, ha="center", va="center",
                fontsize=7.5, fontweight="bold", color="white")
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

    # ── Data rows ─────────────────────────────────────────────────────────────
    for row_i, (_, row) in enumerate(rc.iterrows()):
        grid_row = row_i + 2
        bg_color = "#e8edf3" if row_i % 2 == 0 else "#f5f7fa"

        # Col 0 — District label
        ax = fig.add_subplot(gs[grid_row, 0])
        ax.set_facecolor(bg_color)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.text(0.5, 0.5, f"District {int(row['council_district'])}",
                ha="center", va="center", fontsize=9.5, fontweight="bold", color=NAVY)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Col 1 — Population
        ax = fig.add_subplot(gs[grid_row, 1])
        ax.set_facecolor(bg_color)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        pop = int(row["total_pop"]) if pd.notna(row["total_pop"]) else 0
        ax.text(0.5, 0.5, f"{pop:,}", ha="center", va="center",
                fontsize=8.5, color=SLATE)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Col 2 — % Non-White
        pct_nw = row["pct_nonwhite"] if pd.notna(row["pct_nonwhite"]) else 0
        ax = fig.add_subplot(gs[grid_row, 2])
        ax.set_facecolor(bg_color)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.text(0.5, 0.5, f"{pct_nw:.1f}%", ha="center", va="center",
                fontsize=8.5, color=SLATE)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Col 3 — Stacked demographic bar
        ax = fig.add_subplot(gs[grid_row, 3])
        ax.set_facecolor(bg_color)
        ax.set_xlim(0, 100); ax.set_ylim(0, 1)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        hisp    = row["pct_hispanic"] if pd.notna(row["pct_hispanic"]) else 0
        black   = row["pct_black"]    if pd.notna(row["pct_black"])    else 0
        asian   = row["pct_asian"]    if pd.notna(row["pct_asian"])    else 0
        nh_white_pct = 100 - pct_nw
        other   = max(0, 100 - hisp - black - asian - nh_white_pct)

        segs = [
            (hisp,        "#d55e00", "Hispanic"),
            (black,       "#0072b2", "NH Black"),
            (asian,       "#009e73", "NH Asian"),
            (nh_white_pct,"#cccccc", "NH White"),
            (other,       "#e0c0e0", "Other"),
        ]
        x = 0
        for width, color, label in segs:
            if width > 0.5:
                ax.barh(0.5, width, left=x, height=0.55, color=color, align="center")
                if width > 6:
                    ax.text(x + width / 2, 0.5, f"{width:.0f}%",
                            ha="center", va="center", fontsize=6.5,
                            color="white" if color not in ("#cccccc", "#e0c0e0") else "#444")
                x += width

        # Cols 4–7 — Metric cells with grade color
        for col_offset, (_, metric_key, grade_fn, fmt) in enumerate(metric_cols):
            ax = fig.add_subplot(gs[grid_row, 4 + col_offset])
            val = row[metric_key]
            letter, cell_color = grade_fn(val)
            ax.set_facecolor(cell_color)
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)
            text_color = "white" if cell_color not in (RC_YELLOW,) else "#1a1a1a"
            label_text = fmt.format(val) if pd.notna(val) else "N/A"
            ax.text(0.5, 0.62, label_text, ha="center", va="center",
                    fontsize=9, fontweight="bold", color=text_color)
            ax.text(0.5, 0.22, f"({letter})", ha="center", va="center",
                    fontsize=7, color=text_color, alpha=0.85)
            ax.set_xticks([]); ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)

        # Col 8 — Overall grade
        overall = row["grade_overall"]
        ax = fig.add_subplot(gs[grid_row, 8])
        cell_color = GRADE_COLORS.get(overall, RC_RED)
        ax.set_facecolor(cell_color)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        text_color = "white" if overall not in ("B",) else "#1a1a1a"
        ax.text(0.5, 0.5, overall, ha="center", va="center",
                fontsize=20, fontweight="bold", color=text_color)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_items = [
        mpatches.Patch(color=RC_GREEN,  label="A — Meets standard"),
        mpatches.Patch(color=RC_YELLOW, label="B — Marginal"),
        mpatches.Patch(color=RC_ORANGE, label="C — Below standard"),
        mpatches.Patch(color=RC_RED,    label="D — Poor"),
        mpatches.Patch(color=DARK_RED,  label="F — Critical failure"),
    ]
    demo_items = [
        mpatches.Patch(color="#d55e00", label="Hispanic/Latino"),
        mpatches.Patch(color="#0072b2", label="Non-Hispanic Black"),
        mpatches.Patch(color="#009e73", label="Non-Hispanic Asian"),
        mpatches.Patch(color="#cccccc", label="Non-Hispanic White"),
    ]
    fig.legend(
        handles=legend_items,
        loc="lower left", bbox_to_anchor=(0.04, 0.01),
        ncol=5, fontsize=7.5, framealpha=0.9,
        title="Grade Scale (Response Rate, Ticket Age, Amenity Gap, Burden)",
        title_fontsize=7.5,
    )
    fig.legend(
        handles=demo_items,
        loc="lower right", bbox_to_anchor=(0.97, 0.01),
        ncol=4, fontsize=7.5, framealpha=0.9,
        title="Demographics bar colors",
        title_fontsize=7.5,
    )

    # ── Source note ───────────────────────────────────────────────────────────
    fig.text(
        0.5, 0.003,
        "Sources: Austin 311 Public Data (2023–2026) · CapMetro GTFS (Jan 2026) · "
        "2020 Census Redistricting P.L. 94-171 · Austin Council District Boundaries\n"
        "Grade criteria — Response rate: A≥50% F<15% | Ticket age: A<180d F>550d | "
        "Amenity gap: A=0 F=2 | Tickets/stop: A<20 F>80",
        ha="center", va="bottom", fontsize=6.5, color=SLATE,
    )

    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"  Saved figure → {out_path}")


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Building district report card...")

    demo    = load_demographics()
    transit = load_transit_metrics()
    rc      = build_report_card(demo, transit)

    out_table = ROOT / "output/tables/district_report_card.csv"
    rc.to_csv(out_table, index=False)
    print(f"  Saved table  → {out_table}")
    print()
    print(rc[[
        "council_district", "total_pop", "pct_nonwhite", "pct_hispanic",
        "avg_response_rate_pct", "avg_open_ticket_age_days",
        "avg_amenity_gap", "grade_response", "grade_ticket_age",
        "grade_amenity_gap", "grade_burden", "grade_overall"
    ]].to_string(index=False))

    out_fig = ROOT / "output/figures/district_report_card.png"
    make_figure(rc, out_fig)

    print("\nDone.")
