<!-- markdownlint-disable -->

# Transit Density by Council District

This analysis computes transit density as unique analyzed stops per council district, then pairs density with complaint and unresolved burden.

## Headline

- Highest-density council district in this run: 9
- Unique analyzed stops: 19
- Total calls in council district: 1122
- Unresolved tickets in council district: 873

## Notes

- This uses current analyzed stops, not the complete GTFS stop universe.
- Use this as a council-district-level burden signal for equity discussions.
- If you want full-system density, add full GTFS stops and rerun with complete stop geometry.

## Output Files

- output/tables/transit_density_by_council_district.csv
- output/tables/transit_density_top15_council_districts.csv

## External Benchmark Alignment

Compare this council district output with external indexes (for example, Transit Propensity Index references from external reports) in your equity scorecard narrative.

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
