# CapMetro Service Adequacy and Infrastructure Equity Assessment

## Overview

This assessment examines whether Capital Metro and the City of Austin's high-demand transit stops are visible, safe, accessible, and equitable across council districts. Using public data from 311 complaint records, GTFS service data, and amenity inventories, this baseline identifies where service gaps are concentrated, which stops carry the highest risk, and how complaint burden and response patterns vary across communities.

The analysis covers 25 high-priority bus stops—the busiest transit locations in Austin—and documents amenity deficiencies, unresolved safety and ADA concerns, and long-standing disrepair periods that have persisted for 3+ years without documented repairs.

## Approach

This assessment combines multiple public data sources:

- **311 Complaint Records** (Oct 2021–Apr 2026): 1.25M records across 290 census tracts; complaint categories include safety, maintenance, ADA access, and shelter/seating.
- **GTFS Service Data**: Trip counts and service frequency for high-demand stops.
- **Amenity Inventory**: Physical conditions (shelter, benches, lighting) at each stop.
- **ADA-Related Tickets**: System-wide records of accessibility complaints and their resolution status.
- **Council District Boundaries**: To assess equity across demographic and geographic areas.

**Method:**
Each stop is scored across weighted components: amenity gaps, complaint burden, safety concern density, and ticket age persistence. District-level comparisons examine complaint response rates, unresolved burden, and demographic alignment. All source data, methodology, and code are published to enable independent verification and replication.

## Key Findings

**Amenity Gaps at High-Demand Stops:**
- 80% of analyzed stops are missing shelter.
- 64% of analyzed stops are missing benches.
- These are not peripheral locations—they are the city's busiest transit stops.

**Concentrated Risk:**
- 3 stops are rated CRITICAL liability tier (composite risk score ≥80 of 100).
- The top 5 highest-risk stops account for a disproportionate share of complaint burden and open ADA tickets.
- All 15 severe-gap stops have been in documented disrepair for 3.1–3.3 years.

**Safety & Accessibility Burden:**
- Safety complaints represent 10.65% of analyzed stop-set complaint volume.
- 342 ADA-related records in the baseline window; annual unresolved rate: 83–84%.
- 282 open ADA-flagged tickets system-wide; zero confirmed repairs from either agency.
- 30.9 million cumulative rider-exposure-days occurred during active disrepair periods.

**Complaint Trends:**
- Complaint burden remains elevated: 2023 (443), 2024 (405), 2025 (461), 2026 YTD (118).
- 1,104 of 1,427 high-priority-stop tickets (77.4%) remain open and unresolved.

**Responsibility & Coordination:**
- CapMetro: 82.62% of attributed issues.
- City of Austin: 12.40% of attributed issues.
- Issues span both agencies, requiring coordinated response.

**Equity Discrepancies:**
- All 5 council districts with analyzed stops receive an overall grade of F.
- Districts 3 and 4 serve the highest share of non-white residents (61.7% and 73.9%) and show comparable or worse outcomes than District 9.
- District 4 exhibits the highest phone dependency (65%), meaning residents most affected by service gaps are also least able to report digitally.
- All 25 analyzed stops sit in census tracts with VERY HIGH or EXTREME 311 density (≥2,000 reports/1,000 residents); the Guadalupe/UT corridor reaches 5,975–7,921 reports per 1,000 residents—Austin's highest recorded density.

## Selected Metrics

| Metric | Value | Implication |
|--------|-------|-------------|
| High-priority stops missing shelter | 80% | Basic protection not provided at busiest locations |
| High-priority stops missing benches | 64% | Extended waits without seating |
| CRITICAL-tier risk stops | 3 | Highest liability and safety exposure |
| Stops in 3+ years documented disrepair | 15 of 15 | No documented repairs despite persistent complaints |
| Unresolved ADA-flagged tickets | 282 | Long-term accessibility failures; zero repairs |
| Average ADA annual unresolved rate | 83–84% | Systemic accessibility non-response |
| Unresolved complaint tickets overall | 1,104 / 1,427 | 77.4% backlog across stop set |
| Cumulative rider-exposure-days (disrepair period) | 30.9M | Millions of trips exposed to deficient infrastructure |
| Districts receiving F grade | 5 / 5 | No district shows proportional corrective action |
| Census tracts with EXTREME 311 density | 4 tracts | 5,975–7,921 reports per 1,000 residents (Guadalupe/UT) |

## Implications

**Immediate Risk:**
- Three stops carry near-maximum liability exposure. Prioritized intervention can reduce exposure and demonstrate accountability.
- Unresolved ADA burden creates legal and equity risks.

**Systemic Gaps:**
- 15 stops have been in documented disrepair for 3+ years with zero confirmed repairs from either agency. This indicates a planning and accountability gap at scale, not isolated incidents.
- All 15 severe-gap stops remain absent from any published capital plan or improvement roadmap.

**Equity Impact:**
- Districts serving the highest share of non-white residents show no evidence of corrective action proportional to complaint burden. Absence of improvement indicates a structural equity failure.
- High phone dependency in Districts 3 and 4 means residents most affected have fewer digital reporting channels.
- Severe amenity gaps exist at the highest-demand locations, not at marginal stops. This reflects under-investment in high-equity locations.

**Accountability:**
- Responsibility split (82.62% CapMetro, 12.40% City) requires joint governance and transparent progress tracking. Current baseline shows no monthly progress visibility.

## Next Steps

**Immediate (0–30 Days):**
1. **Establish Joint Taskforce**: Create a CapMetro–City working group with monthly accountability review.
2. **Prioritize Top 10 Stops**: Audit current conditions, repair timeline, and capital-plan inclusion.
3. **Publish Baseline**: Share this assessment and data publicly to enable community and council oversight.

**Short-term (1–3 Months):**
1. **Shelter & Seating Roadmap**: Develop a timeline for shelter installation and bench repairs at 80%+ of high-priority stops.
2. **ADA Response Protocol**: Create a protocol requiring ADA tickets to be triaged, assigned, and resolved within 30 days (or escalated).
3. **Monthly Progress Dashboard**: Publish open-ticket counts, resolved tickets, and repair-completion metrics by stop and district.

**Medium-term (3–12 Months):**
1. **Repair Documentation**: Audit all 15 long-term disrepair stops; document why zero repairs occurred and what is required to complete them.
2. **Equity Progress Scorecard**: Track complaint response rates and resolution times by district; adjust agency resource allocation to close equity gaps.
3. **Digital Access Improvement**: Expand digital 311 reporting in Districts 3, 4, and others with high phone dependency.

**Long-term (12+ Months):**
1. **Capital Plan Integration**: Integrate findings into next CapMetro capital budget cycle; allocate dedicated funding for amenity gaps at high-demand stops.
2. **Continuous Monitoring**: Establish ongoing 311 data pipeline, quarterly equity reporting, and annual risk re-assessment.
3. **Community Accountability**: Present annual progress reports to council and community stakeholders; tie future project approvals to equity outcomes.

## Full Analysis & Data

The complete methodology, all source datasets, reproducible Python analysis scripts, and generated tables and figures are publicly available in the GitHub Repository.

**Quick-Start Files:**
- Evidence matrix with all key findings linked to source data
- Top 10 high-risk stops table
- Council district equity scorecard
- Public safety and liability risk analysis

**Data Sources:**
- 1.25M Austin 311 complaint records (Oct 2021–Apr 2026)
- CapMetro GTFS service data
- City of Austin stop amenity inventory
- ADA-related complaint records

**To Reproduce the Analysis:**
```bash
git clone [GitHub Repository Link]
cd CMTA-Evaluation
pip install -r requirements.txt
bash scripts/run_all.sh
```

All outputs (tables, figures, and narratives) are generated deterministically from the public source data.
