#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
	PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
else
	PYTHON_BIN="python3"
fi

"$PYTHON_BIN" scripts/run_baseline_analysis.py
"$PYTHON_BIN" scripts/geospatial_equity_scaffold.py
"$PYTHON_BIN" scripts/analyze_unresolved_311_by_stop.py
"$PYTHON_BIN" scripts/analyze_ada_incidents.py
"$PYTHON_BIN" scripts/explain_risk_scores.py
"$PYTHON_BIN" scripts/build_equity_progress_scorecard.py
"$PYTHON_BIN" scripts/analyze_problems_by_council_district.py
"$PYTHON_BIN" scripts/analyze_transit_density_by_tract.py
"$PYTHON_BIN" scripts/analyze_gap_analysis.py
"$PYTHON_BIN" scripts/analyze_311_report_density_by_tract.py
"$PYTHON_BIN" scripts/analyze_tract_stop_density_linkage.py
"$PYTHON_BIN" scripts/make_figures.py

echo "All analysis artifacts generated under output/."
