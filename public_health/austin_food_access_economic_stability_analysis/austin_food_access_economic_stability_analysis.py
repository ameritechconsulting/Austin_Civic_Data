import os
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import requests


DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_file(url: str, dest: Path) -> Path:
    if dest.exists():
        return dest
    response = requests.get(url)
    response.raise_for_status()
    dest.write_bytes(response.content)
    return dest


def load_austin_grocery_locations() -> gpd.GeoDataFrame:
    """Load Austin grocery store / food retail points from City of Austin Open Data."""
    # Example URL from City of Austin open data portal. Adjust if the dataset URL differs.
    csv_url = (
        "https://data.austintexas.gov/resource/h3xe-v9k7.csv?$limit=5000"
    )
    dest = DATA_DIR / "austin_grocery_locations.csv"
    if not dest.exists():
        download_file(csv_url, dest)
    df = pd.read_csv(dest)
    if "latitude" in df.columns and "longitude" in df.columns:
        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
            crs="EPSG:4326",
        )
        return gdf
    raise ValueError("Grocery location data does not contain latitude/longitude fields")


def load_census_acs_data(year=2022) -> pd.DataFrame:
    """Retrieve ACS data for SNAP, income, poverty, and childcare proxies."""
    api_key = os.environ.get("CENSUS_API_KEY")
    if not api_key:
        raise EnvironmentError("Set CENSUS_API_KEY in environment to query ACS data.")

    # Example variables; update as needed.
    variables = [
        "NAME",
        "B22001_002E",  # In household receiving food stamps/SNAP
        "B22001_001E",  # Total households
        "B19013_001E",  # Median household income
        "B17001_002E",  # Individuals below poverty level
        "B17001_001E",  # Total individuals
        "B19083_001E",  # Gini index of income inequality
        "B25070_001E",  # Gross rent as a percentage of household income
    ]
    var_string = ",".join(variables)
    url = (
        f"https://api.census.gov/data/{year}/acs/acs5?get={var_string}"
        f"&for=tract:*&in=state:48&in=county:453&key={api_key}"
    )
    response = requests.get(url)
    response.raise_for_status()
    rows = response.json()
    cols = rows[0]
    data = pd.DataFrame(rows[1:], columns=cols)
    data = data.apply(pd.to_numeric, errors="ignore")
    data["snap_rate"] = data["B22001_002E"] / data["B22001_001E"]
    data["poverty_rate"] = data["B17001_002E"] / data["B17001_001E"]
    data = data.rename(
        columns={
            "B19013_001E": "median_household_income",
            "B25070_001E": "rent_burden_pct",
        }
    )
    data["tract_id"] = data["state"].astype(str) + data["county"].astype(str) + data["tract"].astype(str).str.zfill(6)
    return data


def load_austin_tract_shapefile() -> gpd.GeoDataFrame:
    """Download Austin-Travis County census tract boundaries."""
    shapefile_url = (
        "https://www2.census.gov/geo/tiger/TIGER2022/TRACT/tl_2022_48453_tract.zip"
    )
    dest = DATA_DIR / "austin_tracts.zip"
    download_file(shapefile_url, dest)
    gdf = gpd.read_file(dest)
    return gdf.to_crs("EPSG:4326")


def merge_acs_with_tracts(acs: pd.DataFrame, tracts: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    acs["GEOID"] = acs["tract_id"]
    merged = tracts.merge(acs, on="GEOID", how="left")
    return gpd.GeoDataFrame(merged, geometry="geometry", crs="EPSG:4326")


def calculate_food_access(tracts: gpd.GeoDataFrame, grocery: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    grocery = grocery.to_crs(tracts.crs)
    tracts = tracts.copy()
    tracts["centroid"] = tracts.centroid
    centroids = gpd.GeoDataFrame(tracts[["GEOID", "centroid"]], geometry="centroid", crs=tracts.crs)
    grocery_points = grocery.copy()
    grocery_points["geometry"] = grocery_points.geometry

    nearest_distances = []
    for _, row in centroids.iterrows():
        if grocery_points.empty:
            nearest_distances.append(None)
            continue
        distances = grocery_points.geometry.distance(row.geometry)
        nearest_distances.append(distances.min())

    tracts["dist_to_nearest_grocery_meters"] = nearest_distances
    tracts["dist_to_nearest_grocery_miles"] = tracts["dist_to_nearest_grocery_meters"] * 0.000621371
    return tracts


def build_report(merged: gpd.GeoDataFrame) -> pd.DataFrame:
    report = merged[
        [
            "GEOID",
            "NAME",
            "median_household_income",
            "snap_rate",
            "poverty_rate",
            "rent_burden_pct",
            "dist_to_nearest_grocery_miles",
        ]
    ]
    report = report.sort_values(by="snap_rate", ascending=False)
    return report


def plot_food_access_map(merged: gpd.GeoDataFrame, grocery: gpd.GeoDataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 12))
    merged.plot(
        column="snap_rate",
        cmap="OrRd",
        scheme="quantiles",
        k=5,
        edgecolor="gray",
        linewidth=0.4,
        legend=True,
        legend_kwds={"label": "SNAP Rate"},
        ax=ax,
    )
    grocery.plot(ax=ax, color="green", markersize=15, alpha=0.8, label="Grocery/food retail")
    ax.set_title("Austin Census Tracts by SNAP Rate and Grocery Locations")
    ax.axis("off")
    plt.legend()
    plt.tight_layout()
    plt.savefig(DATA_DIR / "austin_snap_food_access_map.png", dpi=200)


def main() -> None:
    print("Loading grocery locations...")
    grocery = load_austin_grocery_locations()
    print(f"Loaded {len(grocery)} grocery or food retail locations.")

    print("Loading ACS data...")
    acs = load_census_acs_data()
    print(f"Loaded ACS records for {len(acs)} census tracts.")

    print("Loading tract boundaries...")
    tracts = load_austin_tract_shapefile()
    print(f"Loaded {len(tracts)} tract boundaries.")

    print("Merging ACS data with tracts...")
    merged = merge_acs_with_tracts(acs, tracts)

    print("Calculating grocery access distances...")
    merged = calculate_food_access(merged, grocery)

    print("Building summary report...")
    report = build_report(merged)
    report.to_csv(DATA_DIR / "austin_food_access_snapshot.csv", index=False)
    print("Saved summary report to data/austin_food_access_snapshot.csv")

    print("Generating food access map...")
    plot_food_access_map(merged, grocery)
    print("Saved food access map to data/austin_snap_food_access_map.png")


if __name__ == "__main__":
    main()
