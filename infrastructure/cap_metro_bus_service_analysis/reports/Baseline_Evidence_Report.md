<!-- markdownlint-disable -->

# Baseline Evaluation of Transit Service Adequacy and Bus Stop Infrastructure Conditions

Date: April 17, 2026  
Prepared for: CMTA and City of Austin baseline accountability review

## Executive Summary

This baseline evaluates whether CMTA and City of Austin transit-related activities are visible, equitable, safe, and aligned with adopted priorities using currently available public datasets.

Key findings from the current baseline run:

- 80% of high-priority stops are missing shelter coverage.
- 64% of high-priority stops are missing bench coverage.
- 10.65% of analyzed complaints are safety-related.
- Responsibility attribution is concentrated with CapMetro (82.62%) versus City of Austin (12.40%) in the summarized issue set.
- 342 ADA-related complaint records appear in the selected baseline window (FY2023-FY2025 + 2026 YTD).

These results indicate concentrated infrastructure deficits at locations with high service intensity and persistent complaint exposure, supporting targeted corrective action planning.

## Purpose and Scope

The analysis establishes a data-driven baseline to identify:

- Infrastructure and service delivery gaps
- Misalignment between commitments and observed conditions
- Accessibility, equity, and safety risk indicators

Scope areas included in this baseline:

- Bus stop infrastructure conditions (amenities and ADA-related indicators)
- Service intensity (GTFS trip_count proxy)
- Public complaint burden (311)
- Jurisdiction split (CapMetro vs City attribution)

## Disclaimer and Methods Statement

This report is a reproducible baseline assessment intended for prioritization and accountability support. It should not be interpreted as a legal determination, a causal proof, or a substitute for engineering field inspection.

How the analysis was produced:
1. Canonical input files were loaded from configured paths.
2. Stop names were normalized for cross-file matching.
3. Indicators were calculated for amenity gaps, complaint burden, safety-related complaints, and ticket-age persistence.
4. A weighted risk framework was used to identify concentrated high-risk stops.
5. Geospatial processing assigned stops to council districts via point-in-polygon joins using official boundary files.
6. Tables and figures were generated from scripts to preserve reproducibility.

Interpretation boundaries:
- GTFS trip metrics are service proxies and do not directly measure observed ridership.
- 311 datasets represent reported issues and may understate unreported conditions.
- Source-system categorization and timestamp conventions can vary.
- Spatial outputs depend on boundary geometry quality and stop coordinate accuracy.

## Data Sources Used

- GTFS-derived stop activity and high-priority stop tables
- Stop amenity condition tables
- 311 complaint summaries, category trends, and detailed records
- ADA violation dataset
- Equity and responsibility summary datasets

## Methods Overview

### 1) Baseline risk index

A stop-level risk index was produced by combining:

- Amenity gap
- Total complaints
- Safety complaints
- Average open ticket age

Weights are configurable in config/analysis_config.yaml.

### 2) Complaint trends over time

Complaint category trends were aggregated by year using 311 category data.

### 3) Responsibility split

CapMetro and City issue attribution shares were computed from responsibility summary records.

### 4) Evidence matrix

A question-to-metric evidence matrix was generated to align audit questions with observable measures and source files.

## Findings

### A. Infrastructure adequacy at high-demand stops

From output/tables/evidence_matrix.csv:

- Share missing shelter: 0.80
- Share missing benches: 0.64

Interpretation:

- Basic rider protections are absent at a large share of high-activity locations.
- This pattern creates weather exposure and accessibility burden risk.

### B. High-risk stop concentration

From output/tables/stop_baseline_risk_index.csv, top-ranked examples include:

- 1609 Lavaca/17th (Midblock)
- Guadalupe/16th Street
- Lavaca/4th
- Guadalupe/W. 21st Street
- UT Dean Keeton Station (NB)

These locations combine high service intensity with high complaint volumes and unresolved condition burden.

### C. Complaint trajectory

From output/tables/yearly_complaint_trends.csv:

- 2023 total: 443
- 2024 total: 405
- 2025 total: 461
- 2026 YTD total: 118

Trend slope in evidence matrix: -91.9 calls/year.

Interpretation caution:

- The slope is influenced by 2026 being partial-year YTD and should not be interpreted as full-year improvement without normalization.

### D. Safety and compliance signals

- Safety complaint share: 0.1065
- ADA-related complaint records in window: 342

Interpretation:

- Safety concerns are a persistent subset of complaint burden.
- ADA-related records indicate material compliance attention needs.

### E. Responsibility alignment

From output/tables/evidence_matrix.csv:

- CapMetro issue share: 0.8262
- City of Austin issue share: 0.1240

Interpretation:

- Most reported issues in the current high-priority summary are attributed to CapMetro categories, with a smaller but relevant City-attributed subset.

## Evidence Matrix

Primary table: output/tables/evidence_matrix.csv

This matrix links each audit question to:

- Metric value
- Source dataset
- Notes on construction and interpretation

## Limitations

- GTFS trip_count measures scheduled service, not observed ridership.
- 311 data captures reported issues only.
- Amenity and complaint records may lag field conditions.
- Spatial council district joins are implemented, but outputs remain dependent on source boundary and coordinate quality.

## Recommendations for Phase 2

1. Validate and harden geospatial joins with periodic boundary/coordinate quality checks.
2. Normalize annual trends for partial-year YTD before trend inference.
3. Integrate budget and performance narrative crosswalk tables.
4. Add formal threshold triggers for ADA and safety escalation.
5. Add field verification sample update cycle for top-risk stops.

## Reproducibility

Run commands:

```bash
python3 scripts/run_baseline_analysis.py
python3 scripts/make_figures.py
```

Artifacts:

- Tables: output/tables/
- Figures: output/figures/

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
