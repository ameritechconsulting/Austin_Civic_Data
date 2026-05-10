<!-- markdownlint-disable -->

# Risk Score Explainer

## Formula

Risk score is the weighted sum of four min-max normalized components:

- amenity_scaled x 0.35
- complaints_scaled x 0.35
- safety_scaled x 0.20
- age_scaled x 0.10

Component weights come from config/analysis_config.yaml.

## How To Read It

- A score closer to 1.0 means the stop is near worst observed values across components.
- A score near 0 means lower relative burden within this analyzed stop set.
- Scores are relative to the current dataset and update when input values change.

## Top 5 Stops And Their Largest Component

- 1609 Lavaca/17th (Midblock): score 0.9996; largest driver = amenity (0.3500)
- Guadalupe/16th Street: score 0.9582; largest driver = amenity (0.3500)
- Lavaca/4th: score 0.9090; largest driver = amenity (0.3500)
- Guadalupe/W. 21st Street: score 0.8603; largest driver = amenity (0.3500)
- UT Dean Keeton Station (NB): score 0.8241; largest driver = amenity (0.3500)

## Output File

- output/tables/risk_score_component_breakdown.csv

---

<!-- ameritech-attribution -->
*Tiffany Moore  •  Ameritech Consulting Group  •  [tiffany@a-techconsulting.com](mailto:tiffany@a-techconsulting.com)  •  [www.a-techconsulting.com](https://www.a-techconsulting.com)  •  [GitHub](https://github.com/ameritechconsulting/cmta-analysis)*
