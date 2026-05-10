from __future__ import annotations

from pathlib import Path
import re

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_TABLES = ROOT / "output" / "tables"
OUTPUT_REPORTS = ROOT / "reports"


def normalize_stop_name(value: str) -> str:
    text = str(value).strip().lower()
    text = text.replace(" station", "")
    text = re.sub(r"\(.*?\)", "", text)
    text = text.replace("&", "/")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_column(df: pd.DataFrame, candidates: list[str]) -> str:
    lowered = {c.lower().strip(): c for c in df.columns}
    for candidate in candidates:
        key = candidate.lower().strip()
        if key in lowered:
            return lowered[key]
    for col in df.columns:
        col_key = col.lower().strip()
        for candidate in candidates:
            if candidate.lower().strip() in col_key:
                return col
    raise KeyError(f"Could not locate any of: {candidates}")


def is_unresolved(status_value: object) -> bool:
    status = str(status_value).strip().lower()
    if not status or status == "nan":
        return False

    unresolved_markers = [
        "open",
        "pending",
        "assigned",
        "in progress",
        "reopen",
        "on hold",
        "new",
    ]
    resolved_markers = ["closed", "resolved", "complete", "completed"]

    if any(marker in status for marker in resolved_markers):
        return False
    return any(marker in status for marker in unresolved_markers)


def min_max_scale(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    low = values.min()
    high = values.max()
    if high == low:
        return pd.Series(np.zeros(len(values)), index=values.index)
    return (values - low) / (high - low)


def main() -> None:
    detailed = pd.read_csv(ROOT / "data/canonical/311_detailed_complaint_report.csv")
    equity = pd.read_csv(ROOT / "data/canonical/equity_analysis_15_stops.csv")

    stop_col = find_column(detailed, ["Stop Name"])
    status_col = find_column(detailed, ["Status", "SR Status"])
    created_col = find_column(detailed, ["Created Date"])

    equity_stop_col = find_column(equity, ["Stop Name"])
    avg_age_col = find_column(equity, ["Avg Open Ticket Age (Days)"])
    response_rate_col = find_column(equity, ["Response Rate"])

    detailed["normalized_stop"] = detailed[stop_col].map(normalize_stop_name)
    detailed["is_unresolved"] = detailed[status_col].map(is_unresolved)
    detailed["created_date"] = pd.to_datetime(
        detailed[created_col],
        errors="coerce",
        format="mixed",
    )

    grouped = (
        detailed.groupby(["normalized_stop", stop_col], as_index=False)
        .agg(
            total_311_calls=(status_col, "count"),
            unresolved_tickets=("is_unresolved", "sum"),
            first_ticket_date=("created_date", "min"),
            last_ticket_date=("created_date", "max"),
        )
        .rename(columns={stop_col: "stop_name"})
    )

    grouped["unresolved_rate"] = grouped["unresolved_tickets"] / grouped["total_311_calls"]

    equity_join = equity[[equity_stop_col, avg_age_col, response_rate_col]].copy()
    equity_join["normalized_stop"] = equity_join[equity_stop_col].map(normalize_stop_name)
    equity_join = equity_join.drop(columns=[equity_stop_col]).drop_duplicates(subset=["normalized_stop"])

    analysis = grouped.merge(equity_join, on="normalized_stop", how="left")
    analysis = analysis.rename(
        columns={
            avg_age_col: "avg_open_ticket_age_days",
            response_rate_col: "response_rate",
        }
    )

    unresolved_scaled = min_max_scale(analysis["unresolved_tickets"])
    rate_scaled = min_max_scale(analysis["unresolved_rate"])
    age_scaled = min_max_scale(analysis["avg_open_ticket_age_days"])

    # Emphasize unresolved volume first, then unresolved rate, then aging signal.
    analysis["unresolved_burden_score"] = (
        unresolved_scaled * 0.5 + rate_scaled * 0.3 + age_scaled * 0.2
    )

    analysis = analysis.sort_values(
        ["total_311_calls", "unresolved_tickets", "unresolved_burden_score"],
        ascending=[False, False, False],
    )

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

    out_cols = [
        "stop_name",
        "total_311_calls",
        "unresolved_tickets",
        "unresolved_rate",
        "avg_open_ticket_age_days",
        "response_rate",
        "unresolved_burden_score",
        "first_ticket_date",
        "last_ticket_date",
    ]

    out_df = analysis[out_cols].copy()
    out_df["unresolved_rate"] = (out_df["unresolved_rate"] * 100).round(1)
    out_df["unresolved_burden_score"] = out_df["unresolved_burden_score"].round(3)
    out_df["response_rate"] = pd.to_numeric(out_df["response_rate"], errors="coerce").round(3)
    out_df["avg_open_ticket_age_days"] = pd.to_numeric(
        out_df["avg_open_ticket_age_days"], errors="coerce"
    ).round(1)

    out_df.to_csv(OUTPUT_TABLES / "311_unresolved_call_burden_by_stop.csv", index=False)

    top_stop = out_df.iloc[0]
    top_stop_row = out_df.head(1)
    top_stop_row.to_csv(OUTPUT_TABLES / "311_top_stop_unresolved_summary.csv", index=False)

    summary = f"""<!-- markdownlint-disable -->

# 311 Unresolved Ticket Burden Summary

This analysis identifies stops with high 311 call volume where tickets remain unresolved (open/pending-style statuses).

## Most impacted stop in this run

- Stop: {top_stop['stop_name']}
- Total 311 calls: {int(top_stop['total_311_calls'])}
- Unresolved tickets: {int(top_stop['unresolved_tickets'])}
- Unresolved rate: {top_stop['unresolved_rate']}%
- Avg open ticket age (days): {top_stop['avg_open_ticket_age_days']}
- Composite unresolved burden score: {top_stop['unresolved_burden_score']}

## Interpretation note

Use this as an accountability and prioritization signal. It indicates complaint burden and unresolved status concentration, but does not on its own prove intent to ignore complaints.

## Output files

- output/tables/311_unresolved_call_burden_by_stop.csv
- output/tables/311_top_stop_unresolved_summary.csv
"""

    OUTPUT_REPORTS.mkdir(parents=True, exist_ok=True)
    (OUTPUT_REPORTS / "311_Unresolved_Burden_Summary.md").write_text(summary, encoding="utf-8")

    print("Unresolved 311 call-burden analysis completed.")
    print(f"Top stop: {top_stop['stop_name']}")
    print(f"Calls: {int(top_stop['total_311_calls'])} | Unresolved: {int(top_stop['unresolved_tickets'])}")


if __name__ == "__main__":
    main()
