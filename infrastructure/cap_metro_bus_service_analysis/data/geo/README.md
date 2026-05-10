<!-- markdownlint-disable -->

# Geospatial Inputs Placeholder

Place boundary files here to enable district and census-tract equity joins.

Expected files (default config):

- council_districts.geojson
- census_tracts.geojson

Current workspace mapping:

- council_districts.geojson was generated from data/geo/Boundaries__City_of_Austin_Council_Districts_20260417.csv (official City of Austin council districts)
- census_tracts.geojson was generated from the official tract source file Boundaries__State_of_Texas_Census_Tracts_(Based_off_2020_Census)_20260417.geojson

Note: official boundary files are now present for both council districts and census tracts, and spatial joins are implemented in scripts/geospatial_equity_scaffold.py.

Minimum requirements:

- Valid polygon geometry
- Consistent CRS (recommended EPSG:4326)
- Stable district/tract identifier fields

Once files are added, run:

```bash
python3 scripts/geospatial_equity_scaffold.py
```

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
