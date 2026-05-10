from __future__ import annotations

from pathlib import Path
from textwrap import fill
from textwrap import shorten

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "output" / "tables"
FIGURES = ROOT / "output" / "figures"

PRIMARY_BLUE = "#002868"
DEEP_NAVY = "#001F3F"
SOFT_WHITE = "#F7F7F2"
MUTED_RED = "#BF0A30"
SLATE_GRAY = "#6B7280"
SAGE_GREEN = "#8AA17D"
GRID_GRAY = "#D1D5DB"


def shorten_stop_name(name: str, width: int = 30) -> str:
    return shorten(str(name), width=width, placeholder="...")


def wrap_public_label(name: str, shorten_width: int = 22, wrap_width: int = 12) -> str:
    short_name = shorten_stop_name(name, width=shorten_width)
    return fill(short_name, width=wrap_width)


def plot_amenity_gap_vs_calls() -> None:
    path = TABLES / "stop_baseline_risk_index.csv"
    df = pd.read_csv(path).nlargest(8, "risk_score").sort_values("risk_score", ascending=False)
    df["trip_count_pct"] = df["trip_count"] / df["trip_count"].max() * 100
    df["total_calls_pct"] = df["total_calls"] / df["total_calls"].max() * 100

    plt.figure(figsize=(13.5, 8.5))
    labels = [wrap_public_label(name, shorten_width=24, wrap_width=11) for name in df["stop_name"]]
    x_positions = list(range(len(df)))
    width = 0.38

    trip_bars = plt.bar(
        [position - width / 2 for position in x_positions],
        df["trip_count_pct"],
        width=width,
        color=PRIMARY_BLUE,
        label="Relative service intensity",
        alpha=0.95,
    )
    call_bars = plt.bar(
        [position + width / 2 for position in x_positions],
        df["total_calls_pct"],
        width=width,
        color=SLATE_GRAY,
        label="Relative 311 complaints",
        alpha=0.95,
    )

    plt.title("Service and 311 complaints at top stops", fontsize=18, weight="bold")
    plt.xlabel("Stop Name", fontsize=13)
    plt.ylabel("Relative scale (highest stop = 100)", fontsize=13)
    plt.xticks(x_positions, labels, rotation=0, ha="center")
    plt.legend(loc="upper right", fontsize=11, title_fontsize=12)
    plt.grid(alpha=0.2, axis="y")
    plt.ylim(0, 122)

    for bar, raw_value in zip(trip_bars, df["trip_count"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.2,
            f"{int(raw_value):,}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    for bar, raw_value in zip(call_bars, df["total_calls"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.2,
            f"{int(raw_value):,}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(FIGURES / "service_vs_complaints_bar.png", dpi=220)
    plt.close()


def plot_yearly_trends() -> None:
    path = TABLES / "yearly_complaint_trends.csv"
    df = pd.read_csv(path).sort_values("year")

    categories = [
        ("complaints_total", "Total", PRIMARY_BLUE),
        ("shelter_complaints", "Shelter", SAGE_GREEN),
        ("bench_complaints", "Benches", SLATE_GRAY),
        ("safety_complaints", "Safety", MUTED_RED),
    ]
    years = df["year"].astype(str).tolist()
    x_positions = list(range(len(df)))
    width = 0.2
    offsets = [-0.3, -0.1, 0.1, 0.3]

    plt.figure(figsize=(12, 8))
    for offset, (column, label, color) in zip(offsets, categories):
        values = df[column]
        bars = plt.bar(
            [position + offset for position in x_positions],
            values,
            width=width,
            label=label,
            color=color,
            alpha=0.95,
        )
        for bar, value in zip(bars, values):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 4,
                str(int(value)),
                ha="center",
                va="bottom",
                fontsize=10,
            )

    plt.title("311 complaints by year and type", fontsize=18, weight="bold")
    plt.xlabel("Year", fontsize=13)
    plt.ylabel("Complaint Count", fontsize=13)
    plt.xticks(x_positions, years)
    plt.legend(title="Category", fontsize=11, title_fontsize=12, loc="upper right")
    plt.grid(alpha=0.2, axis="y")
    plt.ylim(0, max(df["complaints_total"]) * 1.18)
    plt.tight_layout()
    plt.savefig(FIGURES / "complaint_trends_by_year_bar.png", dpi=220)
    plt.close()


def plot_responsibility_split() -> None:
    path = TABLES / "jurisdiction_responsibility_summary.csv"
    df = pd.read_csv(path).nlargest(8, "total_calls").sort_values("total_calls", ascending=False)

    plt.figure(figsize=(13.5, 8.5))
    labels = [wrap_public_label(x, shorten_width=24, wrap_width=11) for x in df["stop_name"]]
    x_positions = list(range(len(df)))
    width = 0.38

    capmetro_bars = plt.bar(
        [position - width / 2 for position in x_positions],
        df["capmetro_share"] * 100,
        width=width,
        label="CapMetro",
        color=PRIMARY_BLUE,
        alpha=0.95,
    )
    city_bars = plt.bar(
        [position + width / 2 for position in x_positions],
        df["city_share"] * 100,
        width=width,
        label="City of Austin",
        color=SAGE_GREEN,
        alpha=0.95,
    )

    plt.title("Who handles complaints at top stops", fontsize=18, weight="bold")
    plt.xlabel("Stop Name", fontsize=13)
    plt.ylabel("Share of Complaints (%)", fontsize=13)
    plt.xticks(x_positions, labels, rotation=0, ha="center")
    plt.legend(loc="upper right", fontsize=11, title_fontsize=12)
    plt.grid(alpha=0.2, axis="y")
    plt.ylim(0, 105)

    for bars in (capmetro_bars, city_bars):
        for bar in bars:
            value = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                value + 0.8,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    plt.tight_layout()
    plt.savefig(FIGURES / "jurisdiction_split_top_stops.png", dpi=220)
    plt.close()


def plot_top_risk_stops_bar() -> None:
    path = TABLES / "stop_baseline_risk_index.csv"
    df = pd.read_csv(path).nlargest(10, "risk_score").sort_values("risk_score", ascending=False)

    plt.figure(figsize=(13.5, 8.5))
    labels = [wrap_public_label(x, shorten_width=24, wrap_width=11) for x in df["stop_name"]]
    x_positions = list(range(len(df)))
    bar_colors = [PRIMARY_BLUE] * len(df)
    if bar_colors:
        bar_colors[0] = MUTED_RED
    bars = plt.bar(x_positions, df["risk_score"], color=bar_colors, alpha=0.95)
    plt.title("Top 10 stops by overall risk", fontsize=18, weight="bold")
    plt.xlabel("Stop Name", fontsize=13)
    plt.ylabel("Risk Score (0-1)", fontsize=13)
    plt.xticks(x_positions, labels, rotation=0, ha="center")
    plt.grid(alpha=0.2, axis="y")
    plt.ylim(0, min(1.05, max(df["risk_score"]) * 1.12))

    for bar, value in zip(bars, df["risk_score"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.01,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.tight_layout()
    plt.savefig(FIGURES / "top10_risk_stops_bar.png", dpi=220)
    plt.close()


def plot_yearly_totals_bar() -> None:
    path = TABLES / "yearly_complaint_trends.csv"
    df = pd.read_csv(path).sort_values("year")

    plt.figure(figsize=(10.5, 7.2))
    ax = sns.barplot(data=df, x="year", y="complaints_total", color=PRIMARY_BLUE)
    ax.set_title("Total 311 complaints by year", fontsize=18, weight="bold")
    ax.set_xlabel("Year", fontsize=13)
    ax.set_ylabel("Total Complaints", fontsize=13)

    for idx, value in enumerate(df["complaints_total"]):
        ax.text(idx, value + 4, str(int(value)), ha="center", fontsize=11)

    plt.grid(alpha=0.2, axis="y")
    plt.ylim(0, max(df["complaints_total"]) * 1.18)
    plt.tight_layout()
    plt.savefig(FIGURES / "complaint_totals_by_year_bar.png", dpi=220)
    plt.close()


def plot_unresolved_311_top10_bar() -> None:
    path = TABLES / "311_unresolved_call_burden_by_stop.csv"
    if not path.exists():
        return

    df = pd.read_csv(path).nlargest(10, "unresolved_tickets").sort_values(
        "unresolved_tickets", ascending=False
    )

    plt.figure(figsize=(13.5, 8.5))
    labels = [wrap_public_label(x, shorten_width=24, wrap_width=11) for x in df["stop_name"]]
    x_positions = list(range(len(df)))
    bar_colors = [PRIMARY_BLUE] * len(df)
    if bar_colors:
        bar_colors[0] = MUTED_RED

    bars = plt.bar(x_positions, df["unresolved_tickets"], color=bar_colors, alpha=0.95)

    plt.title("Top 10 stops by unresolved 311 tickets", fontsize=18, weight="bold")
    plt.xlabel("Stop Name", fontsize=13)
    plt.ylabel("Unresolved Ticket Count", fontsize=13)
    plt.xticks(x_positions, labels, rotation=0, ha="center")
    plt.grid(alpha=0.2, axis="y")
    plt.ylim(0, max(df["unresolved_tickets"]) * 1.22)

    for bar, unresolved, rate in zip(bars, df["unresolved_tickets"], df["unresolved_rate"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            unresolved + 1.2,
            f"{int(unresolved)} ({rate:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(FIGURES / "unresolved_311_top10_bar.png", dpi=220)
    plt.close()


def plot_top_problem_stop_by_district_bar() -> None:
    path = TABLES / "stops_problem_rank_by_council_district.csv"
    if not path.exists():
        return

    df = pd.read_csv(path)
    if "rank_in_district" not in df.columns:
        return

    top_per_district = (
        df[df["rank_in_district"] == 1]
        .sort_values("problem_score", ascending=False)
        .copy()
    )
    if top_per_district.empty:
        return

    top_per_district["district_label"] = (
        "District " + top_per_district["council_district"].astype(str)
    )

    plt.figure(figsize=(12.5, 8.2))
    x_positions = list(range(len(top_per_district)))
    bar_colors = [PRIMARY_BLUE] * len(top_per_district)
    if bar_colors:
        bar_colors[0] = MUTED_RED

    bars = plt.bar(
        x_positions,
        top_per_district["problem_score"],
        color=bar_colors,
        alpha=0.95,
    )

    plt.title("Top problem stop in each council district", fontsize=18, weight="bold")
    plt.xlabel("Council District", fontsize=13)
    plt.ylabel("Problem Score (0-1)", fontsize=13)
    plt.xticks(x_positions, top_per_district["district_label"], rotation=0, ha="center")
    plt.grid(alpha=0.2, axis="y")
    plt.ylim(0, min(1.05, max(top_per_district["problem_score"]) * 1.18))

    for bar, stop_name, score in zip(
        bars,
        top_per_district["stop_name"],
        top_per_district["problem_score"],
    ):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            score + 0.012,
            f"{score:.3f}\n{shorten_stop_name(stop_name, width=22)}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(FIGURES / "district_top_problem_stops_bar.png", dpi=220)
    plt.close()


def plot_district_unresolved_totals_bar() -> None:
    path = TABLES / "council_district_problem_summary.csv"
    if not path.exists():
        return

    df = pd.read_csv(path)
    required_cols = {"council_district", "unresolved_tickets"}
    if not required_cols.issubset(df.columns):
        return

    chart_df = df.sort_values("unresolved_tickets", ascending=False).copy()
    chart_df["district_label"] = "District " + chart_df["council_district"].astype(str)

    plt.figure(figsize=(12, 8))
    x_positions = list(range(len(chart_df)))
    bar_colors = [PRIMARY_BLUE] * len(chart_df)
    if bar_colors:
        bar_colors[0] = MUTED_RED

    bars = plt.bar(
        x_positions,
        chart_df["unresolved_tickets"],
        color=bar_colors,
        alpha=0.95,
    )

    plt.title("Unresolved 311 tickets by council district", fontsize=18, weight="bold")
    plt.xlabel("Council District", fontsize=13)
    plt.ylabel("Total Unresolved Tickets", fontsize=13)
    plt.xticks(x_positions, chart_df["district_label"], rotation=0, ha="center")
    plt.grid(alpha=0.2, axis="y")
    plt.ylim(0, max(chart_df["unresolved_tickets"]) * 1.2)

    for bar, value in zip(bars, chart_df["unresolved_tickets"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 3,
            f"{int(value)}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.tight_layout()
    plt.savefig(FIGURES / "district_unresolved_totals_bar.png", dpi=220)
    plt.close()


def plot_ada_incidents_by_year_bar() -> None:
    path = TABLES / "ada_incidents_by_year.csv"
    if not path.exists():
        return

    df = pd.read_csv(path).sort_values("year")
    if df.empty:
        return

    plt.figure(figsize=(10.5, 7.2))
    x_positions = list(range(len(df)))
    bars = plt.bar(x_positions, df["ada_incidents"], color=PRIMARY_BLUE, alpha=0.95)

    plt.title("ADA-related incidents by year", fontsize=18, weight="bold")
    plt.xlabel("Year", fontsize=13)
    plt.ylabel("Incident Count", fontsize=13)
    plt.xticks(x_positions, [str(int(y)) for y in df["year"]])
    plt.grid(alpha=0.2, axis="y")
    plt.ylim(0, max(df["ada_incidents"]) * 1.2)

    for bar, incidents, unresolved in zip(
        bars,
        df["ada_incidents"],
        df["unresolved_rate_pct"],
    ):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            incidents + 2,
            f"{int(incidents)} ({unresolved:.1f}% unresolved)",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(FIGURES / "ada_incidents_by_year_bar.png", dpi=220)
    plt.close()


def plot_ada_top15_stops_bar() -> None:
    path = TABLES / "ada_top15_stops.csv"
    if not path.exists():
        return

    df = pd.read_csv(path).sort_values("ada_incidents", ascending=False).head(15)
    if df.empty:
        return

    plt.figure(figsize=(14, 8.8))
    labels = [wrap_public_label(x, shorten_width=24, wrap_width=11) for x in df["stop_name"]]
    x_positions = list(range(len(df)))
    bar_colors = [PRIMARY_BLUE] * len(df)
    if bar_colors:
        bar_colors[0] = MUTED_RED

    bars = plt.bar(x_positions, df["ada_incidents"], color=bar_colors, alpha=0.95)

    plt.title("Top 15 stops by ADA-related incidents", fontsize=18, weight="bold")
    plt.xlabel("Stop Name", fontsize=13)
    plt.ylabel("Incident Count", fontsize=13)
    plt.xticks(x_positions, labels, rotation=0, ha="center")
    plt.grid(alpha=0.2, axis="y")
    plt.ylim(0, max(df["ada_incidents"]) * 1.22)

    for bar, count, rate in zip(bars, df["ada_incidents"], df["unresolved_rate_pct"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            count + 1.2,
            f"{int(count)} ({rate:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(FIGURES / "ada_top15_stops_bar.png", dpi=220)
    plt.close()


def plot_transit_density_top15_tracts_bar() -> None:
    path = TABLES / "transit_density_top15_tracts.csv"
    if not path.exists():
        return

    df = pd.read_csv(path)
    if df.empty:
        return

    chart_df = df.sort_values("unique_stops", ascending=False).head(15).copy()
    chart_df["tract_label"] = "Tract " + chart_df["census_tract"].astype(str)

    plt.figure(figsize=(14, 8.5))
    x_positions = list(range(len(chart_df)))
    bar_colors = [PRIMARY_BLUE] * len(chart_df)
    if bar_colors:
        bar_colors[0] = MUTED_RED

    bars = plt.bar(x_positions, chart_df["unique_stops"], color=bar_colors, alpha=0.95)

    plt.title("Top tracts by transit stop density", fontsize=18, weight="bold")
    plt.xlabel("Census Tract", fontsize=13)
    plt.ylabel("Unique Analyzed Stops", fontsize=13)
    plt.xticks(x_positions, chart_df["tract_label"], rotation=40, ha="right")
    plt.grid(alpha=0.2, axis="y")
    plt.ylim(0, max(chart_df["unique_stops"]) * 1.3)

    for bar, stops, calls in zip(bars, chart_df["unique_stops"], chart_df["total_calls"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            stops + 0.08,
            f"{int(stops)} stops\n{int(calls)} calls",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(FIGURES / "transit_density_top15_tracts_bar.png", dpi=220)
    plt.close()


def plot_tract_unresolved_top15_bar() -> None:
    path = TABLES / "transit_density_top15_tracts.csv"
    if not path.exists():
        return

    df = pd.read_csv(path)
    if df.empty:
        return

    chart_df = df.sort_values("unresolved_tickets", ascending=False).head(15).copy()
    chart_df["tract_label"] = "Tract " + chart_df["census_tract"].astype(str)

    plt.figure(figsize=(14, 8.5))
    x_positions = list(range(len(chart_df)))
    bar_colors = [PRIMARY_BLUE] * len(chart_df)
    if bar_colors:
        bar_colors[0] = MUTED_RED

    bars = plt.bar(x_positions, chart_df["unresolved_tickets"], color=bar_colors, alpha=0.95)

    plt.title("Top tracts by unresolved ticket burden", fontsize=18, weight="bold")
    plt.xlabel("Census Tract", fontsize=13)
    plt.ylabel("Unresolved Tickets", fontsize=13)
    plt.xticks(x_positions, chart_df["tract_label"], rotation=40, ha="right")
    plt.grid(alpha=0.2, axis="y")
    plt.ylim(0, max(chart_df["unresolved_tickets"]) * 1.2)

    for bar, unresolved, density in zip(
        bars,
        chart_df["unresolved_tickets"],
        chart_df["unique_stops"],
    ):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            unresolved + 1.2,
            f"{int(unresolved)}\n{int(density)} stops",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(FIGURES / "tract_unresolved_top15_bar.png", dpi=220)
    plt.close()


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    sns.set_theme(
        style="whitegrid",
        context="talk",
        rc={
            "figure.facecolor": SOFT_WHITE,
            "axes.facecolor": SOFT_WHITE,
            "axes.edgecolor": SLATE_GRAY,
            "axes.labelcolor": DEEP_NAVY,
            "axes.titlecolor": DEEP_NAVY,
            "xtick.color": DEEP_NAVY,
            "ytick.color": DEEP_NAVY,
            "grid.color": GRID_GRAY,
            "text.color": DEEP_NAVY,
            "legend.facecolor": SOFT_WHITE,
            "legend.edgecolor": GRID_GRAY,
        },
    )

    plot_amenity_gap_vs_calls()
    plot_yearly_trends()
    plot_responsibility_split()
    plot_top_risk_stops_bar()
    plot_yearly_totals_bar()
    plot_unresolved_311_top10_bar()
    plot_top_problem_stop_by_district_bar()
    plot_district_unresolved_totals_bar()
    plot_ada_incidents_by_year_bar()
    plot_ada_top15_stops_bar()
    plot_transit_density_top15_tracts_bar()
    plot_tract_unresolved_top15_bar()

    print("Figure generation completed.")


if __name__ == "__main__":
    main()
