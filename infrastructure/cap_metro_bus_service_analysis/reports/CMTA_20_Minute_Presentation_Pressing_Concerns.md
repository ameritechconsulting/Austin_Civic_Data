<!-- markdownlint-disable -->

<!-- markdownlint-disable MD022 MD024 MD032 -->

# CMTA + City of Austin Transit Baseline
## 20-Minute Presentation: Most Pressing Concerns

Audience: City leadership, board members, and public accountability stakeholders  
Duration: 20 minutes total

## Slide 1 (2:00) - Why This Baseline Matters
### Title
Baseline Evidence on Transit Stop Conditions, Safety, and Accountability

### Key message
This analysis uses current public data to identify where transit infrastructure risks are highest and where action should be prioritized now.

### Say this
- This is a baseline, not a final audit.
- We focused on publicly available evidence: service intensity, amenity gaps, 311 complaints, and ADA-related records.
- Goal: move from data to practical accountability decisions.

---

## Slide 2 (2:00) - What Data We Used
### Title
Public Data Inputs and Scope

### Show
- top_25_with_amenities.csv
- complaints_all_years.csv
- 311_by_year_and_category.csv
- 311_summary_by_responsibility.csv
- ada_violation_dataset.csv

### Say this
- Time window: FY2023 to FY2025, plus 2026 year-to-date.
- GTFS trip counts are used as service intensity proxy.
- We integrated infrastructure conditions with complaint burden and open ticket age.

---

## Slide 3 (2:00) - Concern 1: Basic Amenities Missing at High-Priority Stops
### Title
High-Demand Stops Have Large Amenity Gaps

### Evidence
From output/tables/evidence_matrix.csv:
- Share missing shelter: 0.80
- Share missing benches: 0.64

### Why this is pressing
- Riders at high-service stops are still exposed to weather and standing burden.
- This directly affects rider experience, safety, and accessibility.

### Visual
Use output/figures/service_vs_complaints_bar.png

---

## Slide 4 (2:00) - Concern 2: Risk Is Concentrated in Specific Stops
### Title
Top-Risk Stops Are Repeatedly Flagged Across Metrics

### Evidence
From output/tables/stop_baseline_risk_index.csv, top risk locations include:
- 1609 Lavaca/17th (Midblock)
- Guadalupe/16th Street
- Lavaca/4th
- Guadalupe/W. 21st Street
- UT Dean Keeton Station (NB)

### Why this is pressing
- These locations combine high service activity, high complaint volume, and unresolved issues.
- Concentration enables targeted intervention planning.

### District lens
- District-level concentration can be shown using each district's top-problem stop profile.
- Tract-level density and unresolved burden provide a neighborhood equity view.

### Visual
Use output/figures/district_top_problem_stops_bar.png
and output/figures/transit_density_top15_districts_bar.png

---

## Slide 5 (2:00) - Concern 3: Persistent Safety and ADA Warning Signals
### Title
Safety and Accessibility Risks Are Not Isolated

### Evidence
From output/tables/evidence_matrix.csv:
- Safety complaint share: 0.1065
- ADA-related records in baseline window: 342

### Why this is pressing
- Safety concerns are a recurring portion of complaint burden.
- ADA-related records suggest continued compliance exposure requiring active mitigation.

### Visual
Use output/figures/ada_top15_stops_bar.png

---

## Slide 6 (2:00) - Concern 4: Yearly Complaint Burden Remains Elevated
### Title
Trends Are Not Yet Reliably Improving

### Evidence
From output/tables/yearly_complaint_trends.csv:
- 2023 total complaints: 443
- 2024 total complaints: 405
- 2025 total complaints: 461
- 2026 YTD complaints: 118

### Why this is pressing
- 2026 is partial-year and should not be compared as full-year improvement.
- Complaint burden remains substantial across complete years.

### Visual
Use output/figures/complaint_trends_by_year_bar.png

---

## Slide 7 (2:00) - Concern 5: Accountability Coordination Must Be Explicit
### Title
Highest-Call Stops Also Show Heavy Unresolved 311 Burden

### Evidence
From output/tables/311_unresolved_call_burden_by_stop.csv:
- 1609 Lavaca/17th (Midblock): 142 calls, 113 unresolved (79.6%)
- Guadalupe/16th Street: 138 calls, 116 unresolved (84.1%)
- Lavaca/4th: 135 calls, 106 unresolved (78.5%)

### Why this is pressing
- Residents repeatedly report issues at the same high-volume locations.
- Open and aging ticket patterns indicate delayed resolution where burden is highest.

### Visual
Use output/figures/unresolved_311_top10_bar.png
and output/figures/district_unresolved_totals_bar.png
and output/figures/district_unresolved_top15_bar.png

---

## Slide 8 (2:00) - What Needs Action in the Next 90 Days
### Title
Immediate Actions for Risk Reduction

### Recommendations
1. Prioritize top 10 risk-index stops for shelter and bench corrective actions.
2. Create a joint CMTA and City resolution tracker for high-call unresolved complaints.
3. Set response time and closure targets for recurring high-risk stops.
4. Publish a monthly public dashboard for top-risk stop progress.
5. Publish A/B/C equity scorecard updates each month using output/tables/equity_progress_scorecard.csv.

### Suggested target
- Reduce high-priority stop missing-shelter share from 0.80 to below 0.60 within one fiscal cycle.

---

## Slide 9a (2:00) - Equity Report Card
### Title
Every District Gets an F — By The Numbers

### Core points
- All 5 analyzed districts receive an overall grade of F.
- District 3 non-white share: 61.7%; District 4 non-white share: 73.9%.
- ADA repairs confirmed by City of Austin: 0 in every district.

### Why this matters
- System failure is broad, but burden concentration is not socially neutral.

---

## Slide 9b (1:30) - Tract Density and Gap Convergence
### Title
The Demand Is Documented: 311 Density by Census Tract

### Core points
- 1,250,625 reports analyzed across 290 Travis County tracts (Oct 2021-Apr 2026).
- All 25 high-demand stops are in VERY HIGH or EXTREME complaint-density tracts.
- Downtown/UT tracts (11.01-11.03 and 337) are among the city's highest-density zones.
- SEVERE GAP stops persist even in the highest-density tracts.

### Why this matters
- Pre-empts the low-demand argument. The gap is operational, not visibility-based.

---

## Slide 9c (1:00) - Digital Divide
### Title
Who Can Report and Who Cannot

### Core points
- Citywide 311 channel split: 62.9% phone and 35.8% digital.
- District 4 has highest phone dependency (65%) and highest mean gap index (54.1).
- District 9 has highest mean tract density (4,382 per 1,000) and 11 SEVERE GAP stops.

### Why this matters
- Phone-dependent districts are likely under-documented in digital-first accountability systems.

---

## Slide 9d (2:00) - What This Baseline Cannot Yet Answer
### Title
Known Gaps and Phase 2 Requirements

### Limitations to state clearly
- GTFS service counts are not measured ridership.
- 311 data reflects reported issues, not all conditions.
- Spatial joins are implemented, but outputs still depend on boundary and coordinate quality.

### Why this matters
- Transparency on limitations increases credibility and prevents over-claiming.

---

## Slide 10 (2:00) - Decision Ask
### Title
Decision Points for Leadership

### Ask for approval
1. Approve focused corrective action plan for top-risk stops.
2. Approve monthly evidence refresh cycle using this reproducible pipeline.
3. Approve unresolved-ticket closure targets and monthly public progress reporting by stop.

### Closing line
This baseline establishes a defensible public-data starting point to move from evidence to measurable accountability.

---

## Slide 11 (1:30) - North Lamar Emergency Accessibility Action
### Title
North Lamar (12300 block): Immediate Sidewalk Gap Escalation

### Situation snapshot
- North Lamar remains a high-risk pedestrian and disability-access corridor where sidewalk gaps persist.
- A new pedestrian beacon (installed Feb 2026) is a positive step but does not resolve missing accessible path segments.

### Immediate public action steps
1. File/confirm Austin 3-1-1 request for the exact segment using "Sidewalk Repair/New Installation."
2. Mark the issue as a life safety risk and document wheelchair-access failure in the request narrative.
3. Escalate to the North Lamar Boulevard Mobility Project at corridors@austintexas.gov.
4. Request District 4 or District 7 office support for an emergency mobility improvement and interim stop-access treatment.
5. File formal ADA complaints with:
	- City Office of Civil Rights: 512-974-3451, officeofcivilrights@austintexas.gov
	- CapMetro ADA Coordinator: 512-389-7583, ccr-accessibility@capmetro.org

### Presenter line
This is where data must become intervention: 3-1-1 documentation, corridor-program escalation, council action, and formal ADA channels should be activated in parallel for this block.

---

## Appendix: Presenter Quick Notes
- Keep discussion anchored to measurable indicators, not anecdotal disputes.
- Emphasize that this is a baseline designed for repeat updates.
- Use plain language for public-facing delivery: shelter, seating, safety, accessibility, response time.
- If asked about geospatial equity maps: confirm district and tract assignment is now implemented.

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
