<!-- markdownlint-disable -->

# Community Meeting Disclaimer (How We Got to This Analysis)

This analysis is a baseline built from public data.

## What we did

1. Selected high-priority stops using service activity and amenity condition files.
2. Combined stop-level records with 311 complaint patterns and ADA-related records.
3. Built repeatable indicators (amenity gaps, complaint burden, safety share, and ticket-age persistence).
4. Added geospatial assignment so each analyzed stop is linked to a council district and census tract.
5. Generated reproducible tables and charts from scripts so results can be rerun and checked.

## What this analysis is and is not

- This is a decision-support baseline, not a legal finding and not a full performance audit.
- It identifies where risk appears concentrated and where follow-up action should be prioritized.
- It does not claim that 311 captures every issue on the ground.

## Data transparency statement

- All indicators in this package are traceable to source files and generated output tables.
- The workflow is script-based and reproducible, so results can be refreshed with new data.

## Important limitations to state clearly

- GTFS trip counts are used as a service proxy, not direct ridership.
- 311 data reflects reported issues, not total condition prevalence.
- Data timing and categorization may differ across source systems.
- Spatial assignment is now implemented, but results still depend on source geometry quality and stop-coordinate quality.

## Plain-language closing line

This is our best public-data baseline to guide action now, with full transparency about methods and limits.

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
