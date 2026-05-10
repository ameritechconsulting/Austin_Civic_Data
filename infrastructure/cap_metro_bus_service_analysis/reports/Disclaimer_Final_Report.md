<!-- markdownlint-disable -->

# Final Report Disclaimer and Methods Summary

## Purpose

This report presents a reproducible baseline assessment of stop-level transit condition risk using publicly available datasets. Findings are intended to support prioritization and accountability decisions and should be interpreted as baseline evidence rather than final causal conclusions.

## How the analysis was produced

1. Canonical input files were defined in configuration and loaded from the active data folder.
2. Stop names were normalized to support cross-file matching.
3. Core indicators were computed from amenity status, complaint burden, safety-related complaints, and ticket-age persistence.
4. A weighted risk framework was applied to identify concentrated high-risk stops.
5. Geospatial processing assigned analyzed stops to council districts and census tracts using point-in-polygon joins against official boundary files.
6. Output tables and figures were generated via scripted runs to preserve reproducibility.

## Data provenance and reproducibility

- Inputs are listed in configuration and in project documentation.
- Outputs are regenerated from scripts rather than manually edited.
- This supports repeat runs as new reporting periods and records are added.

## Scope boundaries

- This baseline does not replace engineering field inspection, legal review, or operational root-cause investigation.
- The analysis is focused on measurable public-data signals and prioritization support.

## Technical limitations

- GTFS trip metrics are service proxies and do not directly measure observed ridership.
- 311 datasets represent reported issues and may understate unreported conditions.
- Source-system categorization and timestamp conventions can vary.
- Spatial outputs depend on boundary geometry quality and stop coordinate accuracy.

## Interpretation guidance

Findings should be read as an evidence-based baseline for prioritization, monitoring, and follow-up validation. Claims beyond observed indicators should be treated as hypotheses for additional investigation.

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
