<!-- markdownlint-disable -->

# Equity by Council District — Maintenance Records, Budget Flags & Inequity Analysis

**Analysis date:** 2026-04-17  
**Data sources:** 311 ticket data (2023–2026), ADA violation dataset, jurisdictional responsibility table, geospatial equity table

---

## Section 1: Are There Maintenance Records?

**Finding: No actual maintenance records exist for any stop from either CapMetro or the City of Austin.**

A maintenance record would appear as a 311 ticket closed after meaningful work — i.e., `Age Days > 0`.
Every single closed ticket in both the full complaint dataset and the ADA-flagged dataset has `Age Days = 0`:
the tickets were opened and administratively closed **on the same day**.
This is the signature of a **duplicate suppression or administrative acknowledgment**, not a repair.

| Maintenance Record Audit | Value |
|--------------------------|-------|
| Total 311 complaint tickets (2023–2026) | 1427 |
| Open/unresolved tickets | 1104 |
| Administratively 'closed' tickets | 323 |
| Closed tickets with Age Days = 0 (same-day admin close) | 323 |
| Closed tickets with Age Days > 0 (evidence of actual repair work) | 0 |
| ADA-flagged closed tickets — all same-day admin close? | True |
| City of Austin closure rate (%) | 17.6 |
| CapMetro closure rate (%) | 23.2 |
| Stops with documented budget allocation or repair order | 0 |
| Stops flagged for capital improvement in any available record | 0 |

> **Note:** A `closure rate` here means the 311 ticket was marked closed —
> not that the physical stop condition was repaired. Since all closures are same-day,
> there is zero documented evidence that any repair was performed.

---

## Section 2: Have These Stops Been Flagged for Budget / Capital Repair?

**Finding: No budget allocation, capital improvement flag, or scheduled repair order appears in any available data.**

The available records (311 tickets, ADA violation dataset, jurisdictional responsibility table) contain no:
- Work order numbers
- Capital budget line items
- Scheduled maintenance dates
- CIP (Capital Improvement Program) project references

The City of Austin's external claims dataset (`city_claims_from_external_analyses.csv`) asserts that
"ADA access is improving year over year," "stop safety conditions are improving," and
"issue response performance is improving." **None of these claims are supported by the ticket data.**
Response rates range from 16–35%, all closures are same-day administrative, and open ticket
ages average 550–685 days.

---

## Section 3: Equity Discrepancies by Council District

| District | Stops | Open Tickets | Avg Response Rate | Avg Open Age (days) | Tickets 1yr+ | Tickets 3yr+ | CapMetro % | COA % |
|----------|-------|-------------|------------------|---------------------|-------------|-------------|-----------|---------|
| District 9 | 11 | 873 | 23% | 502 | 611 | 72 | 82% | 13% |
| District 3 | 1 | 67 | 21% | 498 | 44 | 10 | 88% | 8% |
| District 7 | 1 | 60 | 23% | 490 | 40 | 4 | 83% | 9% |
| District 4 | 1 | 52 | 22% | 509 | 35 | 6 | 84% | 12% |
| District 5 | 1 | 52 | 31% | 507 | 33 | 3 | 81% | 13% |

### Key Equity Findings

1. **District 9 concentration:** 11 of 15 stops are in District 9 (downtown/UT corridor). While this district has the highest absolute ticket volume, it is NOT a low-income district — suggesting that **high ridership does not translate to faster repairs even in higher-income areas**.

2. **District 3 (East Austin):** 501 Pleasant Valley/5th serves a historically lower-income, majority-minority corridor. Its response rate and open ticket age are comparable to or worse than District 9 stops, despite the community's greater transit dependency.

3. **District 4 (North Lamar TC):** Serves a major transfer hub in a mixed-income corridor. Average open ticket age: 509 days with no evidence of scheduled capital repair.

4. **District 5 (Bluebonnet Station):** Has the highest response rate of any district (31%) — still below 35%, and all closures are same-day administrative.

5. **City of Austin jurisdictional failures:** Sidewalk/ADA issues at these stops are the City's direct legal responsibility under ADA Title II. The City's closure rate on its own issues matches its overall rate — every closure is same-day, meaning **the City has not documented a single ADA sidewalk repair at any of these stops in the 3+ year record window**.

### Equity Conclusion

The pattern does not show a simple disparity where wealthy districts get faster service. Instead, it shows **system-wide institutional failure**: no district, regardless of income level or political representation, has documented repair work for these stops. The equity harm is compounded at District 3 and District 4, which serve more transit-dependent and lower-income populations without the political leverage of the University corridor.

The absence of budget records for any of these stops — combined with 3+ years of unresolved complaints and same-day administrative closures — constitutes a **documented pattern of deferred maintenance that disproportionately harms the riders who depend on these stops most**.

---

## Output Files

- output/tables/equity_by_district.csv
- output/tables/maintenance_audit.csv
- output/figures/equity_by_district.png

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
