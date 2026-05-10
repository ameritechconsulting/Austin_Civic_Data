<!-- markdownlint-disable -->

# Scripts Folder

This folder contains reproducible analysis and figure-generation scripts.

## Core Entry Points

- `run_all.sh`: runs the full analysis + figure pipeline.
- `run_baseline_analysis.py`: main baseline processing workflow.
- `make_figures.py`: figure generation.

## Supporting Analyses

- `analyze_unresolved_311_by_stop.py`
- `analyze_disrepair_duration.py`
- `analyze_equity_by_district.py`
- `analyze_311_report_density_by_tract.py`
- `analyze_tract_stop_density_linkage.py`
- `analyze_public_safety_risk.py`

## Usage Notes

- Prefer running `run_all.sh` for a clean full refresh.
- Keep script inputs aligned with `config/analysis_config.yaml` and `config/geospatial_config.yaml`.

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
