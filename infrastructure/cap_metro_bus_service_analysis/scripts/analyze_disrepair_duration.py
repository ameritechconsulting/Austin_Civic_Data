"""
analyze_disrepair_duration.py
─────────────────────────────
Measures how long each high-priority bus stop has been in documented disrepair
using per-ticket complaint data (2023-2026).

Outputs
───────
output/tables/disrepair_duration_by_stop.csv   — per-stop summary
output/tables/disrepair_open_tickets_aged.csv  — per-ticket open-ticket detail
output/figures/disrepair_duration.png          — chart
reports/Disrepair_Duration_Analysis.md         — narrative report
"""
from __future__ import annotations

import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "output" / "tables"
FIGURES = ROOT / "output" / "figures"
REPORTS = ROOT / "reports"
REFERENCE_DATE = datetime.date(2026, 4, 17)


# ── helpers ──────────────────────────────────────────────────────────────────

def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def parse_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ticket_path = ROOT / "archive" / "legacy" / "311_ticket_age_reopens.inserted.csv"
    year_path = ROOT / "data" / "canonical" / "311_by_year_and_category.csv"

    if not ticket_path.exists():
        raise FileNotFoundError(f"Missing {ticket_path}")
    if not year_path.exists():
        raise FileNotFoundError(f"Missing {year_path}")

    tickets = pd.read_csv(ticket_path)
    tickets.columns = tickets.columns.str.strip()

    # Normalise column names
    tickets["stop_name"] = tickets["Stop Name"].str.strip()
    tickets["status"] = tickets["Status"].str.strip().str.lower()
    tickets["created_date"] = parse_date(tickets["Created Date"])
    tickets["close_date"] = parse_date(tickets["Close Date"])
    tickets["age_days"] = to_numeric(tickets["Age Days"])
    tickets["age_years"] = to_numeric(tickets["Age Years"])
    tickets["year"] = to_numeric(tickets["Year"])
    tickets["category"] = tickets["Category"].str.strip()

    ref = pd.Timestamp(REFERENCE_DATE)

    # For open tickets without a recorded age, compute from created_date
    open_mask = tickets["status"] == "open"
    missing_age = tickets["age_days"].isna()
    tickets.loc[open_mask & missing_age, "age_days"] = (
        ref - tickets.loc[open_mask & missing_age, "created_date"]
    ).dt.days
    tickets.loc[open_mask & missing_age, "age_years"] = (
        tickets.loc[open_mask & missing_age, "age_days"] / 365.25
    )

    # Age band labels
    def age_band(days: float) -> str:
        if pd.isna(days):
            return "Unknown"
        if days < 365:
            return "< 1 year"
        if days < 730:
            return "1–2 years"
        if days < 1095:
            return "2–3 years"
        return "3+ years"

    tickets["age_band"] = tickets["age_days"].map(age_band)

    # ── per-stop summary ──────────────────────────────────────────────────────
    stops = []
    for stop, grp in tickets.groupby("stop_name"):
        open_grp = grp[grp["status"] == "open"]
        closed_grp = grp[grp["status"] == "closed"]

        first_complaint = grp["created_date"].min()
        latest_complaint = grp["created_date"].max()
        window_days = (ref - first_complaint).days if pd.notna(first_complaint) else None
        window_years = round(window_days / 365.25, 2) if window_days else None

        open_count = len(open_grp)
        closed_count = len(closed_grp)
        total = len(grp)

        avg_open_age = open_grp["age_days"].mean() if open_count else 0
        max_open_age = open_grp["age_days"].max() if open_count else 0
        oldest_open_date = open_grp["created_date"].min() if open_count else pd.NaT

        tickets_over_1yr = int((open_grp["age_days"] >= 365).sum())
        tickets_over_2yr = int((open_grp["age_days"] >= 730).sum())
        tickets_over_3yr = int((open_grp["age_days"] >= 1095).sum())

        # Year-by-year counts (closed + open)
        yr_counts = grp.groupby("year").size().to_dict()

        stops.append({
            "stop_name": stop,
            "first_complaint_date": first_complaint.date() if pd.notna(first_complaint) else None,
            "latest_complaint_date": latest_complaint.date() if pd.notna(latest_complaint) else None,
            "disrepair_window_days": window_days,
            "disrepair_window_years": window_years,
            "total_tickets": total,
            "open_tickets": open_count,
            "closed_tickets": closed_count,
            "avg_open_ticket_age_days": round(avg_open_age, 1) if open_count else 0,
            "max_open_ticket_age_days": round(max_open_age, 1) if open_count else 0,
            "oldest_open_ticket_date": oldest_open_date.date() if pd.notna(oldest_open_date) else None,
            "open_tickets_over_1yr": tickets_over_1yr,
            "open_tickets_over_2yr": tickets_over_2yr,
            "open_tickets_over_3yr": tickets_over_3yr,
            "calls_2023": int(yr_counts.get(2023, 0)),
            "calls_2024": int(yr_counts.get(2024, 0)),
            "calls_2025": int(yr_counts.get(2025, 0)),
            "calls_2026": int(yr_counts.get(2026, 0)),
        })

    summary = (
        pd.DataFrame(stops)
        .sort_values("disrepair_window_days", ascending=False)
        .reset_index(drop=True)
    )

    # ── open ticket detail ────────────────────────────────────────────────────
    open_detail = (
        tickets[open_mask][
            ["stop_name", "SR Number", "category", "Complaint Description",
             "created_date", "age_days", "age_years", "age_band"]
        ]
        .rename(columns={
            "SR Number": "sr_number",
            "Complaint Description": "complaint_description",
        })
        .sort_values(["stop_name", "age_days"], ascending=[True, False])
        .reset_index(drop=True)
    )

    # ── write tables ──────────────────────────────────────────────────────────
    TABLES.mkdir(parents=True, exist_ok=True)
    summary.to_csv(TABLES / "disrepair_duration_by_stop.csv", index=False)
    open_detail.to_csv(TABLES / "disrepair_open_tickets_aged.csv", index=False)
    print(f"Wrote {len(summary)} stops to disrepair_duration_by_stop.csv")
    print(f"Wrote {len(open_detail)} open tickets to disrepair_open_tickets_aged.csv")

    # ── chart ─────────────────────────────────────────────────────────────────
    FIGURES.mkdir(parents=True, exist_ok=True)

    # Government report-card palette
    # Green = performing (short duration), Yellow = caution, Orange = warning, Red = critical
    RC_GREEN  = "#2e8540"   # USWDS green
    RC_YELLOW = "#fdb81e"   # USWDS gold
    RC_ORANGE = "#e66000"   # USWDS orange
    RC_RED    = "#cc0000"   # USWDS red
    NAVY      = "#1a3a5c"   # government navy (axis labels, spines)
    SLATE     = "#5b616b"   # government mid-gray (gridlines, minor text)
    BG        = "#f5f7fa"   # light government off-white background

    def report_card_color(years: float) -> str:
        if years >= 3:
            return RC_RED
        if years >= 2:
            return RC_ORANGE
        if years >= 1:
            return RC_YELLOW
        return RC_GREEN

    band_order = ["< 1 year", "1–2 years", "2–3 years", "3+ years"]
    band_colors = {
        "< 1 year":  RC_GREEN,
        "1–2 years": RC_YELLOW,
        "2–3 years": RC_ORANGE,
        "3+ years":  RC_RED,
    }

    # Sort worst → best left to right for both charts
    chart_df = summary.dropna(subset=["disrepair_window_years"]).copy()
    chart_df = chart_df.sort_values("disrepair_window_years", ascending=False).reset_index(drop=True)

    # Shorten stop names for x-axis readability
    def shorten(name: str) -> str:
        name = name.replace(" (Midblock)", "").replace(" Station", " Sta.")
        name = name.replace(" Transit Center", " TC").replace(" Street", " St.")
        return name

    labels = [shorten(n) for n in chart_df["stop_name"]]
    x = np.arange(len(labels))
    bar_width = 0.55

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 13))
    fig.patch.set_facecolor(BG)

    # ── Top chart: disrepair window per stop ──────────────────────────────────
    ax1.set_facecolor(BG)
    bar_colors = [report_card_color(v) for v in chart_df["disrepair_window_years"]]
    bars1 = ax1.bar(x, chart_df["disrepair_window_years"], width=bar_width,
                    color=bar_colors, edgecolor="white", linewidth=0.6, zorder=3)

    # Reference lines at 1, 2, 3 years
    for yref, label_txt in [(1, "1 yr"), (2, "2 yrs"), (3, "3 yrs")]:
        ax1.axhline(y=yref, color=SLATE, linestyle="--", linewidth=0.9, alpha=0.7, zorder=2)
        ax1.text(len(x) - 0.45, yref + 0.04, label_txt,
                 color=SLATE, fontsize=8, va="bottom", ha="right")

    # Value labels on top of bars
    for bar, val in zip(bars1, chart_df["disrepair_window_years"]):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.04,
                 f"{val:.1f}y", ha="center", va="bottom",
                 fontsize=8.5, fontweight="bold", color=NAVY)

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=40, ha="right", fontsize=9, color=NAVY)
    ax1.set_ylabel("Years Since First Documented Complaint", fontsize=10, color=NAVY)
    ax1.set_title(
        "Documented Disrepair Window per Stop  (first complaint → April 17, 2026)",
        fontsize=11, fontweight="bold", color=NAVY, pad=10
    )
    ax1.set_ylim(0, chart_df["disrepair_window_years"].max() * 1.22)
    ax1.tick_params(axis="y", labelcolor=NAVY, labelsize=9)
    ax1.yaxis.grid(True, color=SLATE, linewidth=0.5, alpha=0.4, zorder=0)
    ax1.set_axisbelow(True)
    for spine in ax1.spines.values():
        spine.set_edgecolor(SLATE)
        spine.set_linewidth(0.7)

    # Report-card legend
    from matplotlib.patches import Patch
    legend_handles = [
        Patch(facecolor=RC_GREEN,  label="< 1 year  (On track)"),
        Patch(facecolor=RC_YELLOW, label="1–2 years (Needs attention)"),
        Patch(facecolor=RC_ORANGE, label="2–3 years (Failing)"),
        Patch(facecolor=RC_RED,    label="3+ years  (Critical)"),
    ]
    ax1.legend(handles=legend_handles, title="Disrepair Rating",
               title_fontsize=8.5, fontsize=8.5,
               loc="upper right", framealpha=0.9,
               edgecolor=SLATE, labelcolor=NAVY)

    # ── Bottom chart: stacked open tickets by age band ────────────────────────
    ax2.set_facecolor(BG)

    open_agg = (
        tickets[open_mask]
        .groupby(["stop_name", "age_band"])
        .size()
        .unstack(fill_value=0)
    )
    for band in band_order:
        if band not in open_agg.columns:
            open_agg[band] = 0
    open_agg = open_agg[band_order]
    open_agg = open_agg.reindex(chart_df["stop_name"], fill_value=0)

    bottom_vals = np.zeros(len(open_agg))
    for band in band_order:
        vals = open_agg[band].values.astype(float)
        bars2 = ax2.bar(x, vals, width=bar_width, bottom=bottom_vals,
                        color=band_colors[band], edgecolor="white",
                        linewidth=0.6, label=band, zorder=3)
        bottom_vals += vals

    # Total label on top of each stacked bar
    for i, total_val in enumerate(bottom_vals):
        if total_val > 0:
            ax2.text(x[i], total_val + 0.8, str(int(total_val)),
                     ha="center", va="bottom", fontsize=8.5,
                     fontweight="bold", color=NAVY)

    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, rotation=40, ha="right", fontsize=9, color=NAVY)
    ax2.set_ylabel("Number of Open Unresolved Tickets", fontsize=10, color=NAVY)
    ax2.set_title(
        "Open Unresolved Tickets by Age Band  (as of April 17, 2026)",
        fontsize=11, fontweight="bold", color=NAVY, pad=10
    )
    ax2.tick_params(axis="y", labelcolor=NAVY, labelsize=9)
    ax2.yaxis.grid(True, color=SLATE, linewidth=0.5, alpha=0.4, zorder=0)
    ax2.set_axisbelow(True)
    ax2.set_ylim(0, bottom_vals.max() * 1.18)
    for spine in ax2.spines.values():
        spine.set_edgecolor(SLATE)
        spine.set_linewidth(0.7)

    ax2.legend(title="Ticket Age Rating", title_fontsize=8.5, fontsize=8.5,
               loc="upper right", framealpha=0.9,
               edgecolor=SLATE, labelcolor=NAVY)

    fig.suptitle(
        "Bus Stop Disrepair Analysis — High-Priority Stops\nAustin, TX  |  Data: 2023–2026  |  Reference Date: April 17, 2026",
        fontsize=13, fontweight="bold", color=NAVY, y=1.01
    )

    plt.tight_layout(rect=[0, 0, 1, 0.99])
    out_fig = FIGURES / "disrepair_duration.png"
    fig.savefig(out_fig, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved figure to {out_fig}")

    # ── markdown report ───────────────────────────────────────────────────────
    REPORTS.mkdir(parents=True, exist_ok=True)

    top = summary.iloc[0]
    multi_year = summary[summary["disrepair_window_years"] >= 2]
    three_plus = summary[summary["open_tickets_over_3yr"] > 0]
    total_open = int(summary["open_tickets"].sum())
    total_over_1yr = int(summary["open_tickets_over_1yr"].sum())
    total_over_2yr = int(summary["open_tickets_over_2yr"].sum())
    total_over_3yr = int(summary["open_tickets_over_3yr"].sum())

    # Build table rows
    table_rows = []
    for _, row in summary.iterrows():
        table_rows.append(
            f"| {row['stop_name']} "
            f"| {row['first_complaint_date']} "
            f"| {row['disrepair_window_years']:.1f} yrs "
            f"| {int(row['open_tickets'])} "
            f"| {round(row['avg_open_ticket_age_days']):,} days "
            f"| {int(row['open_tickets_over_1yr'])} "
            f"| {int(row['open_tickets_over_3yr'])} |"
        )

    table_header = (
        "| Stop | First Complaint | Window | Open Tickets | Avg Age | Over 1yr | Over 3yr |\n"
        "|------|----------------|--------|-------------|---------|----------|----------|"
    )

    report_lines = [
        "<!-- markdownlint-disable -->",
        "",
        "# Bus Stop Disrepair Duration Analysis",
        "",
        f"**Analysis date:** {REFERENCE_DATE}  ",
        "**Data coverage:** 2023–2026 (per-ticket data; 2021–2022 raw records not yet stop-linked)",
        "",
        "## Summary",
        "",
        f"- **{len(summary)} stops** with documented disrepair complaints.",
        f"- **{len(multi_year)} stops** have a documented complaint window of 2+ years.",
        f"- **{total_open} open/unresolved tickets** remain as of {REFERENCE_DATE}.",
        f"- **{total_over_1yr}** open tickets are over 1 year old ({round(100*total_over_1yr/total_open if total_open else 0)}% of open).",
        f"- **{total_over_2yr}** open tickets are over 2 years old.",
        f"- **{total_over_3yr}** open tickets are over 3 years old.",
        f"- Longest-documented disrepair: **{top['stop_name']}** — first complaint {top['first_complaint_date']}, window **{top['disrepair_window_years']:.1f} years**.",
        "",
        "## How to Read This",
        "",
        "- **Disrepair window** = days from first recorded complaint to April 17, 2026.",
        "- **Open ticket age** = days since ticket was created, for tickets still unresolved.",
        "- Tickets created before 2023 may not appear in the per-ticket dataset; totals represent documented minimum disrepair.",
        "",
        "## Per-Stop Disrepair Table",
        "",
        table_header,
        "\n".join(table_rows),
        "",
        "## Stops with 3+ Year Old Open Tickets",
        "",
    ]

    if len(three_plus) > 0:
        for _, row in three_plus.iterrows():
            report_lines.append(
                f"- **{row['stop_name']}**: {int(row['open_tickets_over_3yr'])} ticket(s) over 3 years old, "
                f"oldest open ticket filed {row['oldest_open_ticket_date']}"
            )
    else:
        report_lines.append("No stops currently have open tickets older than 3 years.")

    report_lines += [
        "",
        "## Year-Over-Year Complaint Trend",
        "",
        "| Stop | 2023 | 2024 | 2025 | 2026 (Jan–Apr) | Trend |",
        "|------|------|------|------|----------------|-------|",
    ]
    for _, row in summary.iterrows():
        yr_vals = [row["calls_2023"], row["calls_2024"], row["calls_2025"], row["calls_2026"]]
        if yr_vals[-2] > yr_vals[0]:
            trend = "↑ Increasing"
        elif yr_vals[-2] < yr_vals[0]:
            trend = "↓ Decreasing"
        else:
            trend = "→ Flat"
        report_lines.append(
            f"| {row['stop_name']} | {yr_vals[0]} | {yr_vals[1]} | {yr_vals[2]} | {yr_vals[3]} | {trend} |"
        )

    report_lines += [
        "",
        "## Data Note",
        "",
        "Per-ticket complaint records are available from 2023 onward for these 15 stops. "
        "The raw Austin 311 Public Data file (`Austin_311_Public_Data_20260412.csv`) contains "
        "records back to 2014 but uses address/geocode fields rather than named stop identifiers, "
        "requiring a geocoded stop-matching step to extend this analysis to 2021–2022. "
        "Disrepair windows reported here are therefore **conservative minimums**.",
        "",
        "## Output Files",
        "",
        "- output/tables/disrepair_duration_by_stop.csv",
        "- output/tables/disrepair_open_tickets_aged.csv",
        "- output/figures/disrepair_duration.png",
    ]

    (REPORTS / "Disrepair_Duration_Analysis.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )
    print("Wrote reports/Disrepair_Duration_Analysis.md")


if __name__ == "__main__":
    main()
