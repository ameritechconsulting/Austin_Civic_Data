<!-- markdownlint-disable -->

# CMTA / City of Austin Transit Baseline — Qualitative Summary

**Prepared:** April 17, 2026  
**Scope:** 15 highest-demand bus stops in Austin, TX | Data window: 2023–2026 (311 tickets), 2026 (amenity conditions)  
**Audience:** Policymakers, board members, community advocates, public comment participants

---

## How to Read This Document

This summary translates quantitative findings into plain language for each section of the analysis.
Every statistic cited here links to a specific output file. All claims are reproducible by rerunning `bash scripts/run_all.sh`.

---

## Section A — Amenity Conditions: What Riders Are Missing Right Now

**Finding: The stops serving the most riders are among the worst-equipped in the system.**

The 15 highest-demand stops — collectively handling hundreds of bus trips per week — were assessed against two baseline amenities: shelter and benches. These are not luxuries. For transit-dependent riders — many of whom are elderly, disabled, or have no alternative transportation — a shelter and a place to sit are functional necessities.

**80% of high-priority stops are missing shelter entirely.**  
**64% are missing benches entirely.**  
All 15 stops have an amenity gap score of 2 (the maximum measured), meaning they are missing both shelter and benches.

The top-ridership stop, 1609 Lavaca/17th (Midblock), serves 2,215 weekly trips. It has no shelter and no benches. The pattern holds across the corridor: Guadalupe/16th Street (2,156 trips/week), Lavaca/4th (2,147 trips/week), and UT Dean Keeton Station (1,843 trips/week) are all in the same condition.

**Why this matters:** CapMetro's own standards recognize that stops above certain ridership thresholds should meet minimum amenity requirements. The data shows that at the system's most-used stops, those standards are not being met, and there is no documented plan to meet them.

*Key statistics:*
- Stops missing shelter: 12 of 15 (80%)
- Stops missing benches: 9.6 of 15 (64%) — rounded from weighted share
- Max weekly trips at a stop with no amenities: 2,215
- All 15 stops score amenity gap = 2 (missing both)
- Source: `output/tables/top10_high_risk_stops_table.csv`, `data/canonical/top_25_with_amenities.csv`

---

## Section B — Complaint Patterns: Are Things Getting Better or Worse?

**Finding: Complaints are not declining. The complaint trend is negative and conditions remain elevated.**

Between 2023 and 2026, 1,427 311 complaint tickets were filed across the 15 analyzed stops. The complaint trend slope is **−91.9 calls per year** — meaning the rate at which complaints are filed has not materially improved despite years of documented community reporting. When corrected for the partial-year nature of 2026 data, the effective annual rate is consistent with prior years.

The breakdown by category tells a more specific story:  
- **Missing shelter complaints** account for the largest share across all stops.  
- **Weather exposure** complaints (riders getting wet, no protection from heat) make up a material portion of every top stop's ticket record.  
- **Safety concerns** — lighting, personal safety at stops, dangerous conditions — represent 10.65% of all complaint volume. At stops serving thousands of weekly trips, this share is operationally significant.

Year-over-year, complaint volume held essentially flat: 2023 (approximately 357 tickets), 2024 (approximately 387 tickets), 2025 (approximately 472 tickets), 2026 partial-year (approximately 82 tickets through April).

**Why this matters:** A sustained complaint volume over 3+ years at the same stops signals that the underlying conditions — missing amenities, exposure risk, safety gaps — have not been addressed. Riders are continuing to file the same complaints year after year with no resolution.

*Key statistics:*
- Total tickets (2023–2026): 1,427
- Complaint trend slope: −91.9 calls/year (not improving)
- Safety complaints as share of total: 10.65%
- Missing shelter as largest complaint category across all 15 stops
- Source: `data/canonical/311_by_year_and_category.csv`, `output/tables/kpi_summary_for_slides.csv`

---

## Section C — Jurisdictional Responsibility: Who Is Accountable for What?

**Finding: CapMetro bears responsibility for most issues, but the City of Austin's share — particularly sidewalk and ADA access — represents a direct legal obligation that is also going unmet.**

Across the 15 stops, responsibility for documented complaints is allocated as follows:  
- **CapMetro: 82.6%** of issues (shelter, benches, weather protection, most safety concerns)  
- **City of Austin: 12.4%** of issues (sidewalk access, ADA compliance, lighting in some cases)  
- **Shared / TBD: ~5%**

This split is important because it clarifies who needs to act. CapMetro's failures are the larger problem in absolute terms — missing shelters and benches are CapMetro infrastructure. But the City of Austin's 12.4% share includes ADA sidewalk access and safety lighting, which carry distinct legal weight under the Americans with Disabilities Act Title II. Federal law does not allow a public entity to claim resource constraints as a defense for ADA non-compliance.

The City's closure rate on its own issues is 17.6% — every single one of those closures is a same-day administrative closure with no documented repair work (see Section F).

**Why this matters:** When two agencies share responsibility for a stop, accountability diffuses. The data here allows specific, assignable claims: CapMetro is responsible for X stops and Y amenities; the City is responsible for Z sidewalks and W lighting issues. Neither agency can shift blame to the other for its own documented failures.

*Key statistics:*
- CapMetro issue share: 82.6% (905 of 1,104 open tickets)
- City of Austin issue share: 12.4% (84 of 1,104 open tickets)
- City of Austin closure rate: 17.6% — all same-day administrative, no repairs
- CapMetro closure rate: 23.2% — all same-day administrative, no repairs
- Source: `data/canonical/jurisdictional_responsibility_15_stops.csv`, `output/tables/maintenance_audit.csv`

---

## Section D — ADA and Compliance Warning Signals

**Finding: ADA-related complaint rates are rising, unresolved rates are worsening, and the City's own claims of improvement are unsupported by the data.**

The ADA incident analysis covers 342 flagged complaint records across 2023–2026. These are complaints that include ADA-related keywords — missing accessible infrastructure, sidewalk obstruction, inaccessible stop conditions — at the 15 high-priority stops.

The unresolved rate has **increased each year**:
- 2023: 78.8% unresolved (82 of 104 ADA tickets)
- 2024: 84.0% unresolved (84 of 100 ADA tickets)
- 2025: 84.3% unresolved (91 of 108 ADA tickets)
- 2026 YTD: 83.3% unresolved (25 of 30 ADA tickets)

The average age of open ADA tickets was 793 days in 2023 — meaning tickets filed in 2023 are, on average, still open. As of April 2026, that cohort is now over 3 years old.

The City of Austin's external claims database asserts "ADA access is improving year over year." The data shows the opposite: the unresolved rate has risen from 78.8% to 84.3% over the same period.

**Why this matters:** ADA Title II is a federal civil rights law. Persistent, documented, unresolved ADA access complaints at high-ridership transit stops — with no evidence of repair — constitute a pattern that disability rights organizations and enforcement agencies can and do act on. This data provides the quantitative foundation for a formal complaint or legal action.

*Key statistics:*
- Total ADA-flagged tickets: 342
- ADA unresolved rate 2023: 78.8%
- ADA unresolved rate 2025: 84.3% (worsening)
- Average age of open ADA tickets (2023 cohort): 793 days
- City claim: "ADA access is improving" — **contradicted by data**
- Source: `data/canonical/ada_violation_dataset.csv`, `output/tables/ada_incidents_by_year.csv`

---

## Section E — Risk Scores: Which Stops Need Immediate Attention

**Finding: The top 10 stops by composite risk score all share the same profile — maximum ridership, maximum amenity gap, elevated complaint volume, and persistent safety concerns.**

The risk index combines four weighted components: weekly trip volume (service demand), total 311 complaints, safety complaint share, and amenity gap. All 15 stops receive the maximum amenity gap score of 2. The differentiation comes from ridership and complaint volume.

**Top 5 stops by risk score:**
1. 1609 Lavaca/17th (Midblock) — risk score 1.000 | 2,215 trips/week | 142 complaints | 19 safety concerns
2. Guadalupe/16th Street — risk score 0.958 | 2,156 trips/week | 138 complaints | 16 safety concerns
3. Lavaca/4th — risk score 0.909 | 2,147 trips/week | 135 complaints | 12 safety concerns
4. Guadalupe/W. 21st Street — risk score 0.860 | 1,994 trips/week | 112 complaints | 13 safety concerns
5. UT Dean Keeton Station (NB) — risk score 0.824 | 1,843 trips/week | 98 complaints | 13 safety concerns

All 10 of the top-risk stops are missing both shelter and benches. The concentration of high-risk stops along the Guadalupe/Lavaca corridor (Council District 9) reflects both the corridor's ridership density and the complete absence of amenity investment along it.

**Why this matters:** Risk scores allow prioritization when resources are limited. These 10 stops represent the most defensible starting point for capital investment — they are simultaneously the busiest, the most complained-about, and the least equipped.

*Key statistics:*
- Top risk score: 1.000 (1609 Lavaca/17th)
- All top 10 risk stops: missing both shelter and benches
- Top 10 stops combined weekly trips: ~18,000+
- Safety concerns in top 10: 127 documented tickets
- Source: `output/tables/top10_high_risk_stops_table.csv`, `output/tables/stop_baseline_risk_index.csv`

---

## Section F — Disrepair Duration and Maintenance Records: How Long Has This Been Happening?

**Finding: Every analyzed stop has been in documented disrepair for at least 3 years. Neither CapMetro nor the City of Austin has a single confirmed repair on record.**

The disrepair duration analysis measures the gap between the first documented complaint at each stop and April 17, 2026. For all 15 stops, that gap is **3.1 to 3.3 years** — every first complaint was filed in January or February 2023, meaning these conditions have been continuously documented since the start of the complaint record window.

**The maintenance record finding is the most significant in this analysis:** Of the 323 tickets recorded as "closed," every single one has an `Age Days` value of 0 — the ticket was opened and closed on the same day. This is an administrative closure pattern: a ticket is acknowledged and immediately marked resolved without any work being performed. There is **zero evidence of actual repair work** at any of the 15 stops from either agency.

The open ticket age breakdown as of April 2026:
- 763 of 1,104 open tickets (69%) are over 1 year old
- Hundreds are over 2 years old
- 95 open tickets across 14 stops are over 3 years old
- Average open ticket age ranges from 532 to 686 days depending on stop

The worst average ticket age by stop is 115 7th/Colorado at 686 days average — meaning the typical open complaint there has been sitting unresolved for nearly two years.

**Why this matters:** The combination of 3+ year disrepair windows and zero confirmed repairs is the definition of deferred maintenance. This is not a resource timing issue — the conditions were documented, the complaints were filed, the tickets were administratively closed, and nothing was fixed. This pattern, applied to ADA-covered infrastructure, creates significant legal exposure for both agencies.

*Key statistics:*
- All 15 stops: disrepair window 3.1–3.3 years
- Confirmed repairs from either agency: **0**
- Tickets closed with Age Days = 0 (admin only): 323 of 323 (100%)
- Open tickets over 1 year old: 763 (69% of all open)
- Open tickets over 3 years old: 95 across 14 of 15 stops
- Worst avg ticket age: 115 7th/Colorado at 686 days
- Source: `output/tables/disrepair_duration_by_stop.csv`, `output/tables/maintenance_audit.csv`

### Additional Qualitative Framing (Public Narrative Version)

1. **The Three-Year Failure Wall**

The data shows a hard floor of neglect: every analyzed stop sits above 1,000 days of documented disrepair (range: 1,131 to 1,201 days, mean: 1,183 days). This is not a backlog spike; it is an institutional pattern.

**Qualitative note:** At stops such as Lavaca/4th, West 38th Station, and Guadalupe/16th Street, maintenance conditions have remained unresolved for nearly three full calendar years. Once a ticket enters this queue, the probability of meaningful resolution appears extremely low.

2. **The "False Resolution" Cycle (Reopened / Duplicate Calls)**

Duplicate-after-closure behavior is strongest where rider traffic is highest.

- Guadalupe/16th Street (2024): 32 duplicate-after-closure records
- Guadalupe/16th Street (2025): 27 duplicate-after-closure records
- Guadalupe/W. 21st Street (2025): 29 duplicate-after-closure records

**Qualitative note:** High duplicate counts indicate repeated rider escalation, not isolated reporting. Riders are filing, seeing closure, and filing again on the same condition. This reflects a broken feedback loop between public reporting and actual field correction.

3. **Zero-Resolution Stagnation**

Closed ADA tickets by year are uniformly same-day closures with no measured age in queue:

- 2023: 22 of 22 closed tickets had Age Days = 0 (100%)
- 2024: 16 of 16 (100%)
- 2025: 17 of 17 (100%)
- 2026 YTD: 5 of 5 (100%)

**Qualitative note:** A persistent 100% same-day closure pattern over four years is a critical red flag. The system appears to be reducing administrative inventory rather than reducing physical hazard conditions.

4. **High-Traffic Abandonment**

The worst records occur at central, visible, high-traffic nodes rather than low-activity stops:

- Guadalupe/16th Street: liability score 99.4 (CRITICAL), 2.55M rider-exposure-days
- 1609 Lavaca/17th (Midblock): 2,215 trips/week, 2.64M rider-exposure-days, HIGH liability tier
- North Lamar Transit Center: average open ticket age 665 days at a major transfer hub
- Republic Square Station (NB) and UT Dean Keeton Station (NB): multi-year disrepair windows with elevated unresolved burden

**Qualitative note:** This is not a visibility problem. High-profile locations with sustained rider demand are still not being repaired. The pattern points to operational capacity and accountability failure, not lack of awareness.

> "At several top stops, average open ticket age remains in multi-year territory while all 15 analyzed stops exceed 1,000 disrepair days and documented repairs remain at zero."

---

## Section G — Equity by Council District: Is the Burden Shared Fairly?

**Finding: The equity failure is system-wide, not district-specific — but it falls hardest on Districts 3 and 4, which serve more transit-dependent and lower-income populations.**

The five council districts with high-priority stops in this analysis are Districts 3, 4, 5, 7, and 9. Their comparative profiles:

| District | Stops | Open Tickets | Avg Response Rate | Avg Ticket Age | Context |
|----------|-------|-------------|------------------|----------------|---------|
| District 9 | 11 | 873 | 23% | 502 days | Downtown/UT corridor; higher-income, high-ridership |
| District 3 | 1 | 67 | 21% | 499 days | East Austin; lower-income, majority-minority, transit-dependent |
| District 7 | 1 | 60 | 23% | 490 days | North Austin; Northcross corridor |
| District 4 | 1 | 52 | 22% | 509 days | North Lamar TC; mixed-income, major transfer hub |
| District 5 | 1 | 52 | 31% | 507 days | South Austin; Bluebonnet — highest response rate, still 507-day avg age |

The most important finding here is **uniformity**: no district is getting meaningfully faster service. Response rates range from 21% to 31%, all closures are administrative, and average ticket ages are 490–509 days across every district. This is not a story of one district being favored — it is a story of institutional failure that affects everyone.

However, **the equity harm is not equal**. District 3 (East Austin's 501 Pleasant Valley/5th) serves a corridor where residents have fewer transportation alternatives, lower average income, and less political leverage than the University corridor. The 501 Pleasant Valley/5th stop has the second-highest number of open tickets with a 3+ year duration (10 tickets), and its responsible-party mix shows CapMetro at 88.2% — meaning the majority of unresolved issues are CapMetro's direct responsibility on a stop serving a low-income, majority-minority community.

District 4's North Lamar Transit Center is a major regional transfer hub with a 509-day average ticket age and no budget flag of any kind. For riders connecting across the system, this is a critical piece of infrastructure being maintained at the same near-zero level as all other stops.

The City of Austin's own jurisdictional issues — sidewalk access and ADA compliance — show zero confirmed repairs across all five districts. The City's legal obligations under ADA Title II do not vary by district or income level. The uniform non-performance represents an equal-opportunity failure with unequal impacts.

*Key statistics:*
- Districts with high-priority stops: 5 (Districts 3, 4, 5, 7, 9)
- District 9 open tickets: 873 (79% of system total)
- District 3 response rate: 21% — comparable to District 9 despite community context
- District 4 avg ticket age: 509 days — longest of any single-stop district
- District 5 response rate: 31% — best in analysis; still 507-day avg open age
- City of Austin ADA repairs confirmed by district: 0 in all districts
- Source: `output/tables/equity_by_district.csv`, `output/figures/equity_by_district.png`

---

## Section H — 311 Density by Tract and Digital Access: Is Demand Actually Visible?

**Finding: Demand is fully documented at these stops; the ongoing gap is not a low-volume or low-visibility issue.**

- 1,250,625 reports analyzed (Oct 2021-Apr 2026) across 290 Travis County census tracts.
- All 25 high-demand stops are in VERY HIGH or EXTREME complaint-density tracts (>=2,000 reports per 1,000 residents).
- Downtown/UT tracts (11.01-11.03 and 337) are among the city's highest-density complaint zones.
- District 9 has the highest mean tract density (4,382 per 1,000) and still contains 11 SEVERE GAP stops.
- District 4 has the highest mean gap index (54.1) and the highest phone dependency (65% phone).
- Citywide 311 channel mix is 62.9% phone and 35.8% digital, so phone-dependent districts are more likely to be under-documented in digital-first monitoring.
- Bottom line: this is not a demand-visibility problem; it is a persistent supply and maintenance-response problem.
- Source: `output/tables/311_report_density_by_tract.csv`, `output/tables/311_report_density_by_district.csv`, `output/tables/stop_tract_density_linkage.csv`, `output/tables/equity_tract_density_summary.csv`, `output/figures/stop_tract_density_combined.png`, `output/figures/311_digital_divide_by_district.png`

---

## Summary of City Claims vs. Measured Data

The City of Austin's public-facing claims (sourced from `data/external_reports/city_claims_from_external_analyses.csv`) are directly testable against this dataset:

| City Claim | Measured Finding | Assessment |
|-----------|-----------------|------------|
| "ADA access is improving year over year" | ADA unresolved rate rose from 78.8% (2023) to 84.3% (2025) | **Contradicted** |
| "Stop safety conditions are improving" | Safety complaints steady at 10.65% of all complaints; no year shows decline | **Contradicted** |
| "Issue response performance is improving" | Overall unresolved rate 76.7%; all closures same-day administrative; 0 confirmed repairs | **Contradicted** |

All three public claims are contradicted by the data. This is not a matter of interpretation — the metrics the City would use to demonstrate improvement (ADA resolution rates, safety complaint share, ticket closure rates) all move in the wrong direction or remain static across the analysis period.

---

## What This Analysis Does Not Claim

This analysis is grounded in public 311 complaint data, which reflects **reported and filed conditions**, not a complete physical inspection of every stop. The following limitations apply:

1. Complaint records begin in 2023 for per-ticket analysis; the actual disrepair window may extend earlier.
2. The 15 stops analyzed are the highest-demand stops, not all stops system-wide.
3. "Administrative closure" is inferred from Age Days = 0; it is possible that a small number of same-day closures represent rapid response, but the scale (100% of all closures) makes this statistically implausible as an explanation for all cases.
4. Budget and capital improvement data is drawn only from what is available in public records — a formal public records request may reveal additional documentation.

---

## Output Files Referenced in This Summary

| File | Section |
|------|---------|
| `output/tables/top10_high_risk_stops_table.csv` | A, E |
| `output/tables/kpi_summary_for_slides.csv` | A, B, C |
| `output/tables/evidence_matrix.csv` | All |
| `data/canonical/311_by_year_and_category.csv` | B |
| `data/canonical/jurisdictional_responsibility_15_stops.csv` | C |
| `output/tables/ada_incidents_by_year.csv` | D |
| `output/tables/equity_progress_scorecard.csv` | D, Summary |
| `output/tables/stop_baseline_risk_index.csv` | E |
| `output/tables/disrepair_duration_by_stop.csv` | F |
| `output/tables/maintenance_audit.csv` | F, C |
| `output/tables/equity_by_district.csv` | G |
| `output/tables/311_report_density_by_tract.csv` | H |
| `output/tables/311_report_density_by_district.csv` | H |
| `output/tables/stop_tract_density_linkage.csv` | H |
| `output/tables/equity_tract_density_summary.csv` | H |
| `output/figures/disrepair_duration.png` | F |
| `output/figures/equity_by_district.png` | G |
| `output/figures/stop_tract_density_combined.png` | H |
| `output/figures/311_digital_divide_by_district.png` | H |
| `output/figures/public_safety_risk.png` | E, D |
| `output/figures/district_report_card.png` | G |
| `output/tables/public_safety_risk_by_stop.csv` | E, D |
| `output/tables/liability_exposure_summary.csv` | E, D |
| `output/tables/district_report_card.csv` | G |

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
