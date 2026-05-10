<!-- markdownlint-disable -->

# Council District Stop Problem Analysis

This analysis ranks stops by problem concentration and summarizes burden by council district.

## Method

Problem score weights:
- 40% baseline risk score
- 20% total 311 calls
- 20% unresolved 311 tickets
- 10% safety concerns
- 10% amenity gap

All components are min-max scaled before weighting.

## Highest-Burden District In This Run

- Council District: 3
- Avg problem score: 0.665
- Total calls: 85
- Total unresolved tickets: 67
- Top problem stop: 501 Pleasant Valley/5th

## Top 10 Stops By Problem Score

- District 9: 1609 Lavaca/17th (Midblock) (score 0.995, calls 142, unresolved 113, unresolved rate 79.6%)
- District 9: Guadalupe/16th Street (score 0.962, calls 138, unresolved 116, unresolved rate 84.1%)
- District 9: Lavaca/4th (score 0.9, calls 135, unresolved 106, unresolved rate 78.5%)
- District 9: Guadalupe/W. 21st Street (score 0.827, calls 112, unresolved 91, unresolved rate 81.2%)
- District 9: UT Dean Keeton Station (NB) (score 0.757, calls 98, unresolved 70, unresolved rate 71.4%)
- District 9: Guadalupe/4th (score 0.724, calls 92, unresolved 75, unresolved rate 81.5%)
- District 9: Vic Mathias/Auditorium Shores (SB) (score 0.705, calls 95, unresolved 71, unresolved rate 74.7%)
- District 9: Republic Square Station (NB) (score 0.672, calls 82, unresolved 64, unresolved rate 78.0%)
- District 3: 501 Pleasant Valley/5th (score 0.665, calls 85, unresolved 67, unresolved rate 78.8%)
- District 9: 115 7Th/Colorado (score 0.645, calls 88, unresolved 68, unresolved rate 77.3%)

## 311 Density and Digital Access Context (FY2022-FY2026)

- 1,250,625 records (Oct 2021-Apr 2026) were used to map district burden into 290 Travis County tracts.
- All 25 high-demand stops are in VERY HIGH or EXTREME complaint-density tracts.
- District 9 has the highest mean tract density (4,382 per 1,000) and still contains 11 SEVERE GAP stops.
- District 4 has the highest mean gap index (54.1) and highest phone dependency (65% phone), indicating likely under-documentation in digital-first channels.
- Districts 3 and 5 also show high-density, high-gap conditions, confirming the burden is multi-district.
- This supports the stop ranking above: severe conditions are concentrated in high-demand geographies, not low-demand outliers.
- The district pattern is therefore operational, not visibility-driven.

## Output Files

- output/tables/stops_problem_rank_by_council_district.csv
- output/tables/council_district_problem_summary.csv
- output/tables/311_report_density_by_district.csv
- output/tables/equity_tract_density_summary.csv
- output/tables/gap_analysis_with_tract_density.csv
- output/figures/district_top_problem_stops_bar.png
- output/figures/district_unresolved_totals_bar.png
- output/figures/311_digital_divide_by_district.png
- output/figures/stop_tract_density_combined.png

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
