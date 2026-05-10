<!-- markdownlint-disable -->

# CMTA + City of Austin Transit Baseline Evidence Package

## Start Here

This workspace is now organized around the current analysis only.

If you want the fastest possible entry point, open USE_THESE_FIRST.md.

If you are preparing for the meeting, open PRESENTATION_PACK.md.

If you want a polished deck outline to paste into slides, open reports/presentation_versions/CMTA_Board_Ready_Slide_Outline.md.

If you only want to understand or rerun the baseline, focus on these folders:

- data/canonical/: the source files actively used by the pipeline
- scripts/: the analysis and chart code
- output/tables/: generated tables for findings and slides
- output/figures/: generated figures for findings and slides
- reports/: presentation and narrative materials

Everything older, duplicated, or not used by the current pipeline has been moved out of the way into archive/legacy/ or data/reference/.

For archived raw-source provenance, see archive/sources/INDEX.md.

## Purpose

This repository provides a reproducible baseline analysis of whether Capital Metro and the City of Austin's transit-related activities are visible, safe, accessible, and accountable in public data.

## What The Analysis Uses

The current pipeline uses only these canonical inputs:

- data/canonical/top_25_with_amenities.csv
- data/canonical/high_priority_stops_311_analysis.csv
- data/canonical/311_detailed_complaint_report.csv
- data/canonical/311_by_year_and_category.csv
- data/canonical/311_summary_by_responsibility.csv
- data/canonical/jurisdictional_responsibility_15_stops.csv
- data/canonical/equity_analysis_15_stops.csv
- data/canonical/ada_violation_dataset.csv
- data/canonical/stop_amenities_2026.csv

## What The Analysis Answers

1. Are high-demand stops missing basic amenities?
2. Are complaint patterns improving or staying elevated over time?
3. How are issues split between CapMetro and the City of Austin?
4. Are there ADA-related warning signals in the current baseline window?
5. Which stops and districts show the highest unresolved ADA and complaint burden?
6. How is each stop risk score calculated and what drives it most?
7. How do measured indicators compare with city-facing equity/progress claims (A/B/C scorecard)?
8. How long have these stops been in documented disrepair, and is there any maintenance record?
9. Are there equity discrepancies by council district in complaint response and repair accountability?

## Folder Guide

- config/: file mappings and scoring settings
- data/canonical/: active source data
- data/reference/: useful supporting files not required by the main pipeline
- archive/legacy/: older, duplicate, raw, or superseded files kept for record
- scripts/: reproducible analysis code
  - run_baseline_analysis.py — main baseline pipeline
  - analyze_unresolved_311_by_stop.py — 311 unresolved burden
  - analyze_ada_incidents.py — ADA incident analysis
  - analyze_problems_by_council_district.py — district-level problems
  - analyze_transit_density_by_tract.py — transit density by council district
  - analyze_disrepair_duration.py — disrepair window and ticket age analysis
  - analyze_equity_by_district.py — equity discrepancies by council district
  - build_equity_progress_scorecard.py — A/B/C scorecard
  - explain_risk_scores.py — risk score explainer
  - make_figures.py — chart generation
  - geospatial_equity_scaffold.py — geospatial joins
  - extract_external_pdf_claims.py — city claims extraction
- output/: generated tables and figures
- reports/: policy report and presentation material
- notebooks/: notebook version of the workflow

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Analysis

```bash
bash scripts/run_all.sh
```

Or run the two scripts directly:

```bash
python3 scripts/run_baseline_analysis.py
python3 scripts/make_figures.py
```

## Main Outputs

Most users only need these files:

For presentation prep, use PRESENTATION_PACK.md together with the files listed below.

### Tables

- output/tables/evidence_matrix.csv
- output/tables/stop_baseline_risk_index.csv
- output/tables/top10_high_risk_stops_table.csv
- output/tables/kpi_summary_for_slides.csv
- output/tables/ada_incidents_by_year.csv
- output/tables/ada_top15_stops.csv
- output/tables/risk_score_component_breakdown.csv
- output/tables/equity_progress_scorecard.csv

### Figures

- output/figures/top10_risk_stops_bar.png
- output/figures/complaint_totals_by_year_bar.png
- output/figures/jurisdiction_split_top_stops.png
- output/figures/ada_incidents_by_year_bar.png
- output/figures/ada_top15_stops_bar.png
- output/figures/transit_density_top15_tracts_bar.png
- output/figures/tract_unresolved_top15_bar.png

## External PDF Analyses

You can include additional city or consultant analyses in PDF format.

1. Put PDFs in data/external_reports/pdf/
2. Run:

```bash
python3 scripts/extract_external_pdf_claims.py
```

This creates output/tables/external_pdf_claim_snippets.csv so claims and language from external analyses can be integrated into the equity scorecard workflow.

## Geospatial Equity Scaffold

Add boundary files to data/geo/ and run:

```bash
python3 scripts/geospatial_equity_scaffold.py
```

This creates placeholder-ready outputs for district and tract summaries:

- output/tables/stop_geospatial_equity.csv
- output/tables/district_equity_summary.csv
- output/tables/tract_equity_summary.csv

Note: the current scaffold prepares the join-ready tables and summary structure; full spatial joins require boundary files and geometry-enabled processing in the next phase.

## Method Summary

### 1) Stop-level baseline risk index

Merges high-priority service stops with complaints and open-ticket-age indicators.

Risk score components (weighted in config):

- Amenity gap (missing shelter/bench signal)
- Total complaint burden
- Safety concern burden
- Ticket age persistence

### 2) Yearly complaint trajectory

Aggregates complaint counts by year and category from data/canonical/311_by_year_and_category.csv to evaluate trend direction.

### 3) Responsibility split

Builds CapMetro vs City share metrics from data/canonical/311_summary_by_responsibility.csv.

### 4) Evidence matrix

Creates a concise table linking each audit question to a measurable indicator and source file.

## Important Limitations

- GTFS trip_count is a service proxy, not observed ridership.
- 311 reflects reported conditions, not full condition prevalence.
- Amenities and operational conditions may lag current field reality.
- Spatial equity crosswalks (stop-to-census geographies) are not fully implemented in this baseline package.

## Intended Use

This package is designed as baseline evidence for internal policy review, board discussion, and potential formal submission workflows.

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
