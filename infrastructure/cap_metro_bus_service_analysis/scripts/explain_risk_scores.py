from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "analysis_config.yaml"
INPUT_PATH = ROOT / "output" / "tables" / "stop_baseline_risk_index.csv"
OUTPUT_TABLES = ROOT / "output" / "tables"
OUTPUT_REPORTS = ROOT / "reports"


def min_max_scale(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    low = values.min()
    high = values.max()
    if high == low:
        return pd.Series(np.zeros(len(values)), index=values.index)
    return (values - low) / (high - low)


def main() -> None:
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    w = cfg["weights"]

    df = pd.read_csv(INPUT_PATH)

    df["amenity_scaled"] = min_max_scale(df["amenity_gap"])
    df["complaints_scaled"] = min_max_scale(df["total_calls"])
    df["safety_scaled"] = min_max_scale(df["safety_concerns"])
    df["age_scaled"] = min_max_scale(df["avg_open_ticket_age_days"])

    df["amenity_component"] = df["amenity_scaled"] * float(w["amenity_gap_weight"])
    df["complaints_component"] = df["complaints_scaled"] * float(w["complaints_weight"])
    df["safety_component"] = df["safety_scaled"] * float(w["safety_weight"])
    df["age_component"] = df["age_scaled"] * float(w["age_weight"])

    df["reconstructed_risk_score"] = (
        df["amenity_component"]
        + df["complaints_component"]
        + df["safety_component"]
        + df["age_component"]
    )

    df["score_delta"] = (df["risk_score"] - df["reconstructed_risk_score"]).round(8)

    out_cols = [
        "stop_id",
        "stop_name",
        "risk_score",
        "reconstructed_risk_score",
        "score_delta",
        "amenity_gap",
        "total_calls",
        "safety_concerns",
        "avg_open_ticket_age_days",
        "amenity_scaled",
        "complaints_scaled",
        "safety_scaled",
        "age_scaled",
        "amenity_component",
        "complaints_component",
        "safety_component",
        "age_component",
    ]

    out = df[out_cols].copy().sort_values("risk_score", ascending=False)

    numeric_cols = [
        "risk_score",
        "reconstructed_risk_score",
        "amenity_scaled",
        "complaints_scaled",
        "safety_scaled",
        "age_scaled",
        "amenity_component",
        "complaints_component",
        "safety_component",
        "age_component",
    ]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce").round(4)

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORTS.mkdir(parents=True, exist_ok=True)

    out.to_csv(OUTPUT_TABLES / "risk_score_component_breakdown.csv", index=False)

    top = out.head(5)
    lines = [
        "<!-- markdownlint-disable -->",
        "",
        "# Risk Score Explainer",
        "",
        "## Formula",
        "",
        "Risk score is the weighted sum of four min-max normalized components:",
        "",
        "- amenity_scaled x 0.35",
        "- complaints_scaled x 0.35",
        "- safety_scaled x 0.20",
        "- age_scaled x 0.10",
        "",
        "Component weights come from config/analysis_config.yaml.",
        "",
        "## How To Read It",
        "",
        "- A score closer to 1.0 means the stop is near worst observed values across components.",
        "- A score near 0 means lower relative burden within this analyzed stop set.",
        "- Scores are relative to the current dataset and update when input values change.",
        "",
        "## Top 5 Stops And Their Largest Component",
        "",
    ]

    for _, row in top.iterrows():
        components = {
            "amenity": float(row["amenity_component"]),
            "complaints": float(row["complaints_component"]),
            "safety": float(row["safety_component"]),
            "age": float(row["age_component"]),
        }
        largest = max(components, key=components.get)
        lines.append(
            f"- {row['stop_name']}: score {row['risk_score']:.4f}; largest driver = {largest} ({components[largest]:.4f})"
        )

    lines.extend(
        [
            "",
            "## Output File",
            "",
            "- output/tables/risk_score_component_breakdown.csv",
        ]
    )

    (OUTPUT_REPORTS / "Risk_Score_Explainer.md").write_text("\n".join(lines), encoding="utf-8")

    print("Risk score explainer completed.")
    print("Wrote output/tables/risk_score_component_breakdown.csv")


if __name__ == "__main__":
    main()
