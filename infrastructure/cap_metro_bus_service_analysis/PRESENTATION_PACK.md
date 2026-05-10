<!-- markdownlint-disable -->

# Presentation Pack

This file tells you exactly what to use for the 20-minute presentation.

## The 3 Numbers To Repeat Verbally
Use these three numbers repeatedly because they are the clearest and strongest:

1. 80%
Meaning: share of high-priority stops missing shelter.
Source: output/tables/evidence_matrix.csv

2. 64%
Meaning: share of high-priority stops missing benches.
Source: output/tables/evidence_matrix.csv

3. 342
Meaning: ADA-related complaint records in the baseline window.
Source: output/tables/evidence_matrix.csv

## Best 3 Charts For The Meeting
1. output/figures/top10_risk_stops_bar.png
Use for: showing where the most urgent problems are concentrated.

2. output/figures/complaint_totals_by_year_bar.png
Use for: showing complaint burden remains elevated.

3. output/figures/jurisdiction_split_top_stops.png
Use for: showing why CMTA and City coordination matters.

## Slide-By-Slide Pack

### Slide 1 - Why This Matters
Use:
- No chart required
- Supporting file: output/tables/evidence_matrix.csv

Say:
- This is a baseline built from public data.
- The point is to identify the most urgent stop-level risks and the clearest accountability gaps.

Repeat:
- This is a starting point for action, not a final audit.

### Slide 2 - What Data Was Used
Use:
- No chart required
- Supporting source file list from USE_THESE_FIRST.md

Show these source files:
- data/canonical/top_25_with_amenities.csv
- data/canonical/high_priority_stops_311_analysis.csv
- data/canonical/311_summary_by_responsibility.csv
- data/canonical/ada_violation_dataset.csv

Say:
- The analysis combines high-priority stop activity, complaint burden, responsibility, and ADA-related records.

### Slide 3 - Basic Amenity Gaps
Use:
- Main chart: output/figures/top10_risk_stops_bar.png
- Supporting table: output/tables/kpi_summary_for_slides.csv

Say:
- 80% of high-priority stops are missing shelter.
- 64% of high-priority stops are missing benches.
- These are not peripheral stops. These are high-service locations.

Repeat:
- 80% missing shelter.
- 64% missing benches.

### Slide 4 - Top-Risk Stops
Use:
- Main table: output/tables/top10_high_risk_stops_table.csv
- Optional supporting chart: output/figures/top10_risk_stops_bar.png

Show these top 5 stops:
1. 1609 Lavaca/17th (Midblock)
2. Guadalupe/16th Street
3. Lavaca/4th
4. Guadalupe/W. 21st Street
5. UT Dean Keeton Station (NB)

Say:
- The risk is concentrated.
- That means targeted intervention is possible.

### Slide 5 - Safety and ADA Concerns
Use:
- Supporting table: output/tables/evidence_matrix.csv
- Supporting table: output/tables/kpi_summary_for_slides.csv

Say:
- Safety complaints make up 10.65% of complaint volume in the analyzed stop set.
- There are 342 ADA-related records in the baseline window.

Repeat:
- 342 ADA-related records.

### Slide 5a - Public Safety Risk & Liability
Use:
- Main chart: output/figures/public_safety_risk.png
- Supporting table: output/tables/public_safety_risk_by_stop.csv
- Supporting table: output/tables/liability_exposure_summary.csv

Say:
- 3 stops are rated CRITICAL liability tier (composite score ≥ 80 of 100).
- 30.9 million cumulative rider-exposure-days during the active disrepair period.
- 282 open ADA-flagged tickets system-wide; 0 confirmed repairs from either agency.
- Guadalupe/16th Street scores 99.4 — near-maximum liability — due to 116 open ADA tickets and 22 zero-day administrative closures.

Repeat:
- 0 confirmed repairs.
- 30.9 million rider-exposure-days.

### Slide 6 - Complaint Burden Over Time
Use:
- Main chart: output/figures/complaint_totals_by_year_bar.png
- Supporting table: output/tables/yearly_complaint_trends.csv

Say:
- Complaint burden remains substantial across full years.
- 2026 is year-to-date only and should not be treated as a full-year improvement.

Use these numbers:
- 2023: 443
- 2024: 405
- 2025: 461
- 2026 YTD: 118

### Slide 7 - Responsibility and Coordination
Use:
- Main chart: output/figures/jurisdiction_split_top_stops.png
- Supporting table: output/tables/top15_responsibility_table.csv

Say:
- CapMetro accounts for 82.62% of summarized issue attribution.
- City of Austin accounts for 12.40%.
- The issues are not entirely one-agency problems. Coordination is required.

Repeat:
- 82.62% CapMetro.
- 12.40% City.

### Slide 8 - Immediate Actions
Use:
- Supporting file: reports/CMTA_20_Minute_Presentation_Pressing_Concerns.md
- Supporting file: reports/CMTA_20_Minute_Presenter_Cheat_Sheet.md

Say:
1. Prioritize the top 10 risk stops.
2. Create a joint CMTA-City safety and ADA tracker.
3. Publish monthly progress updates.

### Slide 9 - What This Baseline Does Not Yet Cover
Use:
- No chart required
- Supporting file: README.md

Say:
- GTFS trip counts are service proxy, not ridership.
- 311 data reflects reported issues, not all conditions.
- Geospatial district and tract joins are now implemented; output quality still depends on source geometry and coordinate quality.

### Slide 9a - Equity by Council District
Use:
- Main chart: output/figures/district_report_card.png
- Supporting chart: output/figures/equity_by_district.png
- Supporting table: output/tables/district_report_card.csv

Say:
- All 5 council districts with analyzed stops receive an overall grade of F.
- Districts 3 and 4 serve the highest share of non-white residents (61.7% and 73.9%) and have comparable or worse outcomes than District 9.
- No district shows evidence of targeted corrective action proportional to complaint burden or demographic need.

Repeat:
- All 5 districts: F.

### Slide 9b - Tract Density & Gap Convergence
Use:
- Main chart (simple): output/figures/stop_tract_density_simple.png
- Main chart: output/figures/stop_tract_density_combined.png
- Alt scatter: output/figures/stop_tract_density_scatter.png
- Supporting table: output/tables/stop_tract_density_linkage.csv

Say:
- 1.25M 311 records across 290 Travis County tracts document where demand is highest.
- Every one of the 25 high-demand stops sits in a tract rated VERY HIGH or EXTREME density (≥2,000 reports per 1,000 residents).
- The Guadalupe/UT corridor (Tracts 11.01–11.03, 337) reaches 5,975–7,921 reports per 1,000 residents — the highest density in the county.
- SEVERE GAP stops exist across the full density spectrum. This is not a reporting gap — it is an agency supply gap.

Repeat:
- All 15 SEVERE GAP stops: zero capital plan. All tracts: VERY HIGH or EXTREME density.

### Slide 9c - Digital Divide
Use:
- Main chart: output/figures/311_digital_divide_by_district.png
- Supporting table: output/tables/311_report_density_by_district.csv

Say:
- 62.9% of all 311 reports citywide are filed by phone.
- District 4 = 65% phone dependency (highest). District 9 = 58% digital (lowest phone dependency).
- Phone-dominant districts produce fewer digital data points — so lower 311 counts in Districts 3 and 4 do not mean fewer problems.
- The accountability mechanism itself has a structural access gap.

Repeat:
- Low digital access = undercounted in the record. District 4's gap is likely worse than data shows.

### Slide 10 - Decision Ask
Use:
- No chart required
- Supporting file: reports/CMTA_20_Minute_Presentation_Pressing_Concerns.md

Ask for:
1. Approval of focused corrective action for top-risk stops.
2. Approval of monthly evidence refresh and reporting.
3. Approval of monthly district and tract density monitoring (including digital access split) in the standing report.

## Fastest Build Option
If you are assembling slides quickly, use these files in this order:

1. reports/presentation_versions/CMTA_Board_Ready_Slide_Outline.md
2. PRESENTATION_PACK.md
3. reports/presentation_versions/CMTA_20_Minute_Slide_Layout.md
4. output/figures/top10_risk_stops_bar.png
5. output/figures/complaint_totals_by_year_bar.png
6. output/figures/jurisdiction_split_top_stops.png
7. output/tables/top10_high_risk_stops_table.csv
8. output/tables/kpi_summary_for_slides.csv
9. output/figures/public_safety_risk.png
10. output/figures/district_report_card.png
11. output/figures/stop_tract_density_combined.png
12. output/figures/311_digital_divide_by_district.png
13. output/figures/stop_tract_density_simple.png
14. output/figures/311_annual_volume_by_district_heatmap.png
15. output/figures/311_annual_volume_priority_districts_heatmap.png

## If You Only Have 5 Minutes
Use only:
- output/figures/top10_risk_stops_bar.png
- output/figures/complaint_totals_by_year_bar.png
- output/tables/kpi_summary_for_slides.csv
- reports/presentation_versions/CMTA_5_Minute_Executive_Brief.md

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
