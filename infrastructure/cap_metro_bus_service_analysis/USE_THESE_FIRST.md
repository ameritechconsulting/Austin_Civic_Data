<!-- markdownlint-disable -->

# Use These First

This is the shortest path through the project.

## If You Only Look At 4 Source Files
These are the main files driving the current analysis:

1. data/canonical/top_25_with_amenities.csv
What it does: combines high-priority stop activity with amenity conditions.

2. data/canonical/high_priority_stops_311_analysis.csv
What it does: summarizes 311 complaint burden for the high-priority stops.

3. data/canonical/311_summary_by_responsibility.csv
What it does: shows how complaint responsibility is split between CapMetro and the City of Austin.

4. data/canonical/ada_violation_dataset.csv
What it does: captures ADA-related complaint records used for compliance warning signals.

## If You Only Look At 10 Output Files
These are the most useful outputs for understanding findings quickly:

1. output/tables/evidence_matrix.csv
Why it matters: the clearest single summary of the main findings and their source files.

2. output/tables/top10_high_risk_stops_table.csv
Why it matters: shows the stops that most urgently need attention.

3. output/tables/kpi_summary_for_slides.csv
Why it matters: gives the headline numbers for reports and presentations.

4. output/tables/stop_baseline_risk_index.csv
Why it matters: full ranked stop-level risk table behind the summary outputs.

5. output/tables/311_unresolved_call_burden_by_stop.csv
Why it matters: ranks stops by unresolved 311 complaint burden to show where resident complaints remain open.

6. output/tables/council_district_problem_summary.csv
Why it matters: shows which council districts carry the highest stop-level problem burden and the top stop in each district.

7. output/tables/ada_incidents_by_year.csv
Why it matters: gives yearly ADA-related incident counts and unresolved rates.

8. output/tables/risk_score_component_breakdown.csv
Why it matters: explains exactly how each stop's risk score was built from weighted components.

9. output/tables/equity_progress_scorecard.csv
Why it matters: provides an A/B/C equity progress scorecard aligned to city-facing claims and measured indicators.

10. output/tables/transit_density_by_council_district.csv
Why it matters: shows council-district-level transit stop density paired with complaint and unresolved burden for equity framing.

11. output/tables/disrepair_duration_by_stop.csv
Why it matters: documents how long each stop has been in active disrepair — all 15 stops are at 3+ years with zero documented repairs.

12. output/tables/equity_by_district.csv
Why it matters: aggregates complaint burden, response rates, and responsible-party mix by council district for equity comparison.

13. output/tables/maintenance_audit.csv
Why it matters: audits whether any closed tickets represent actual repair work — finding is zero confirmed repairs across all stops and both agencies.

14. output/tables/external_pdf_claim_snippets.csv
Why it matters: keyword-matched sentences from 8 agency PDFs (City CIP memos, CapMetro CFO report, audit plans). Zero of 39 matched snippets reference bus stop capital improvements or any of the 15 high-demand stops — confirms the gap analysis supply-side zero is accurate, not a data gap.

15. output/tables/311_report_density_by_tract.csv
Why it matters: 1.25M 311 records assigned to 290 Travis County census tracts (Oct 2021–Apr 2026). Includes total reports, reports/1,000 residents, reports/km², phone share, and digital share per tract. All 290 tracts received at least 1 report; top tracts (11.01, 11.02, 11.03, 337) are the Guadalupe/UT corridor — same geography as the CRITICAL-tier stops.

16. output/tables/stop_tract_density_linkage.csv
Why it matters: Links each of the 25 high-demand stops to its census tract and appends that tract's 311 density data. Every high-demand stop sits in a tract with VERY HIGH or EXTREME density (≥2,000 reports/1k residents). District 9 stops average 4,382 reports/1k.

17. output/tables/gap_analysis_with_tract_density.csv
Why it matters: Gap analysis enriched with tract density, digital access tier, and population — the full supply-demand-density picture in one file for each of the 25 stops.

18. output/tables/equity_tract_density_summary.csv
Why it matters: District-level summary combining tract 311 density, mean gap index, phone/digital share, and severe-gap stop count. District 4 has the highest gap index (54.1) paired with HIGH phone dependency (65% phone), meaning residents most affected are also least able to report digitally.

## The 10 Charts To Use In Your Presentation
These are the easiest charts for a general audience to read:

1. output/figures/top10_risk_stops_bar.png
Best use: shows where the most urgent stop-level problems are concentrated.

2. output/figures/complaint_totals_by_year_bar.png
Best use: shows that complaint burden remains substantial across full years.

3. output/figures/jurisdiction_split_top_stops.png
Best use: shows why CapMetro and City coordination matters.

4. output/figures/unresolved_311_top10_bar.png
Best use: shows where the largest unresolved 311 complaint burdens are concentrated.

5. output/figures/district_top_problem_stops_bar.png
Best use: compares each district's top problem stop so district-level burden can be discussed clearly.

6. output/figures/district_unresolved_totals_bar.png
Best use: shows which council districts carry the largest unresolved 311 ticket burden.

7. output/figures/ada_incidents_by_year_bar.png
Best use: shows year-by-year ADA-related incident burden and unresolved rates.

8. output/figures/ada_top15_stops_bar.png
Best use: shows which stops have the highest ADA-related incident concentration.

9. output/figures/transit_density_top15_districts_bar.png
Best use: shows which council districts have the highest analyzed transit stop density.

10. output/figures/district_unresolved_top15_bar.png
Best use: shows which council districts carry the largest unresolved complaint burden.

11. output/figures/disrepair_duration.png
Best use: shows how long each stop has been in documented disrepair using a report-card color scale (green→red).

12. output/figures/equity_by_district.png
Best use: four-panel view of open tickets, response rates, ticket age, and responsible-party mix by council district.

13. output/figures/public_safety_risk.png
Best use: four-panel public safety and liability analysis — composite liability score per stop, safety/ADA ticket breakdown, score component breakdown, and cumulative rider-exposure-days. 3 stops are CRITICAL tier (score ≥80), 2 are HIGH.

14. output/figures/district_report_card.png
Best use: multi-column visual report card combining demographic composition per council district with 4 graded transit metrics (response rate, ticket age, amenity gap, tickets per stop). All 5 analyzed districts currently receive an overall F.

15. output/figures/311_report_density_top25.png
Best use: dual bar chart showing top 25 census tracts by both population-normalized and land-area density. Documents that the Guadalupe/UT corridor (Tracts 11.01–11.03, 337) is Austin's highest-density 311 reporting zone.

16. output/figures/311_digital_divide_by_district.png
Best use: stacked phone/digital/other chart by council district across all 1.25M FY2022–2026 records. District 4 = 65% phone (highest phone dependency); District 9 = 58% digital (most digitally engaged). Critical for equity framing.

17. output/figures/stop_tract_density_scatter.png
Best use: scatter plot with one point per stop — tract density on x-axis, gap index on y-axis, colored by gap tier. Shows that SEVERE GAP stops (dark red) are spread across the full density range, proving gaps are not explained by low demand — they exist even at the city's highest-density locations.

18. output/figures/stop_tract_density_combined.png
Best use: 4-panel figure combining all tract-density themes: (1) tract density at each stop, (2) gap index by stop, (3) digital divide by district, (4) density vs. gap dual-axis by district. Best single slide for the density-equity-gap argument.

19. output/figures/stop_tract_density_simple.png
Best use: easiest single chart for board/public audiences. One horizontal bar per stop showing tract reports per 1,000 residents, with a clear 2,000 threshold marker and simple severe-gap highlighting.

20. output/figures/311_annual_volume_by_district_heatmap.png
Best use: easiest annual district trend view. Heatmap cells show report counts by district and fiscal year (with FY2026 clearly marked as partial), making cross-district and year-over-year comparisons faster than a 10-line trend chart.

21. output/figures/311_annual_volume_priority_districts_heatmap.png
Best use: high-clarity board slide focused only on priority districts (3, 4, 5, 7, 9). Best option when you want clean year-over-year comparison without lower-priority district noise.

## Headline Findings From The Current Run
- 80% of high-priority stops are missing shelter.
- 64% of high-priority stops are missing benches.
- Safety complaints are 10.65% of complaint volume in the analyzed stop set.
- CapMetro accounts for 82.62% of summarized issue attribution.
- City of Austin accounts for 12.40% of summarized issue attribution.
- ADA-related records in the baseline window: 342; unresolved rate 83–84% annually.
- All 15 high-priority stops have been in documented disrepair for 3.1–3.3 years.
- 1,104 of 1,427 tickets (77.4%) remain open and unresolved.
- 0 tickets from either agency were closed with Age Days > 0 — no confirmed repairs documented.
- 0 stops are flagged for budget allocation or capital improvement in any available record.
- District 9 carries 873 open tickets across 11 stops; Districts 3 and 4 serve lower-income, transit-dependent populations with comparable or worse response rates.

## Top 5 High-Risk Stops Right Now
1. 1609 Lavaca/17th (Midblock)
2. Guadalupe/16th Street
3. Lavaca/4th
4. Guadalupe/W. 21st Street
5. UT Dean Keeton Station (NB)

## If You Need To Re-Run The Analysis
```bash
bash scripts/run_all.sh
```

This now runs baseline analysis, unresolved 311 burden analysis, figure generation, and geospatial joins.

## If You Want The Main Presentation Files
- reports/presentation_versions/CMTA_Board_Ready_Slide_Outline.md
- reports/CMTA_20_Minute_Presentation_Pressing_Concerns.md
- reports/CMTA_20_Minute_Presenter_Cheat_Sheet.md
- reports/presentation_versions/CMTA_20_Minute_Slide_Layout.md
- reports/presentation_versions/CMTA_5_Minute_Executive_Brief.md
- reports/presentation_versions/CMTA_Public_Comment_Version.md

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
