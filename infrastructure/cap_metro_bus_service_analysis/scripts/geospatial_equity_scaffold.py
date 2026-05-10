from __future__ import annotations

import json
from pathlib import Path
import re

import numpy as np
import pandas as pd
import yaml
from shapely.geometry import Point, shape


ROOT = Path(__file__).resolve().parent.parent
CFG_PATH = ROOT / "config" / "geospatial_config.yaml"


def normalize_stop_name(value: str) -> str:
    text = str(value).strip().lower()
    text = text.replace(" station", "")
    text = re.sub(r"\(.*?\)", "", text)
    text = text.replace("&", "/")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_column(df: pd.DataFrame, candidates: list[str]) -> str:
    lowered = {c.lower().strip(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower().strip() in lowered:
            return lowered[candidate.lower().strip()]
    for col in df.columns:
        for candidate in candidates:
            if candidate.lower().strip() in col.lower().strip():
                return col
    raise KeyError(f"Could not locate any of: {candidates}")


def try_find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    try:
        return find_column(df, candidates)
    except KeyError:
        return None


def load_config() -> dict:
    with CFG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_geojson_features(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if data.get("type") != "FeatureCollection":
        raise ValueError(f"Expected FeatureCollection at {path}")
    return data.get("features", [])


def find_property_key(features: list[dict], candidates: list[str]) -> str:
    lowered_candidates = {c.lower().strip() for c in candidates}
    for feature in features:
        props = feature.get("properties", {})
        for key in props.keys():
            if key.lower().strip() in lowered_candidates:
                return key
    available = set()
    for feature in features[:25]:
        available.update(feature.get("properties", {}).keys())
    raise KeyError(f"Could not locate any of {candidates}. Available sample keys: {sorted(available)}")


def assign_point_to_polygon(point: Point, prepared_features: list[tuple[object, object]]) -> object:
    # include boundary points with intersects instead of strict contains
    for geom, value in prepared_features:
        if geom.intersects(point):
            return value
    return np.nan


def build_prepared_features(features: list[dict], id_key: str) -> list[tuple[object, object]]:
    prepared: list[tuple[object, object]] = []
    for feature in features:
        geom_data = feature.get("geometry")
        if not geom_data:
            continue
        props = feature.get("properties", {})
        geom = shape(geom_data)
        prepared.append((geom, props.get(id_key)))
    return prepared


def build_coordinates_table(stops: pd.DataFrame, cfg: dict, stops_id_col: str | None) -> pd.DataFrame:
    lat_candidates = cfg["join_settings"]["stop_latitude_column_candidates"]
    lon_candidates = cfg["join_settings"]["stop_longitude_column_candidates"]

    lat_col = try_find_column(stops, lat_candidates)
    lon_col = try_find_column(stops, lon_candidates)
    if lat_col and lon_col:
        cols = ["normalized_stop", lat_col, lon_col]
        if stops_id_col:
            cols.insert(0, stops_id_col)
        coords = stops[cols].copy()
        rename = {lat_col: "latitude", lon_col: "longitude"}
        if stops_id_col:
            rename[stops_id_col] = "stop_id"
        coords = coords.rename(columns=rename)
    else:
        coord_file = ROOT / cfg["inputs"].get("coordinate_file", "data/canonical/stop_amenities_2026.csv")
        coord_df = pd.read_csv(coord_file)
        coord_name_col = find_column(coord_df, ["stop_name", "Stop Name", "STOP_NAME"])
        coord_id_col = try_find_column(coord_df, ["stop_id", "Stop ID", "STOP_ID"])
        coord_lat_col = find_column(coord_df, lat_candidates + ["LATITUDE"])
        coord_lon_col = find_column(coord_df, lon_candidates + ["LONGITUDE"])

        coord_df["normalized_stop"] = coord_df[coord_name_col].map(normalize_stop_name)
        cols = ["normalized_stop", coord_lat_col, coord_lon_col]
        if coord_id_col:
            cols.insert(0, coord_id_col)
        coords = coord_df[cols].copy()
        rename = {coord_lat_col: "latitude", coord_lon_col: "longitude"}
        if coord_id_col:
            rename[coord_id_col] = "stop_id"
        coords = coords.rename(columns=rename)

    coords["latitude"] = pd.to_numeric(coords["latitude"], errors="coerce")
    coords["longitude"] = pd.to_numeric(coords["longitude"], errors="coerce")
    return coords


def main() -> None:
    cfg = load_config()

    stops = pd.read_csv(ROOT / cfg["inputs"]["stops_file"])
    complaints = pd.read_csv(ROOT / cfg["inputs"]["complaints_file"])
    equity = pd.read_csv(ROOT / cfg["inputs"]["equity_file"])

    stops_name_col = find_column(stops, ["stop_name", "Stop Name"])
    stops_id_col = try_find_column(stops, ["stop_id", "Stop ID", "STOP_ID"])
    comp_name_col = find_column(complaints, ["stop_name", "Stop Name"])
    equity_name_col = find_column(equity, ["stop_name", "Stop Name"])

    stops["normalized_stop"] = stops[stops_name_col].map(normalize_stop_name)
    complaints["normalized_stop"] = complaints[comp_name_col].map(normalize_stop_name)
    equity["normalized_stop"] = equity[equity_name_col].map(normalize_stop_name)

    total_calls_col = find_column(complaints, ["Total Calls (2021-2025)", "Total Calls"])
    amenity_gap_col = find_column(stops, ["amenity_gap", "Amenity Gap"])
    weekly_trips_col = find_column(equity, ["Weekly Trips", "trip_count"])

    stop_cols = [stops_name_col, "normalized_stop", amenity_gap_col]
    if stops_id_col:
        stop_cols.insert(0, stops_id_col)

    joined = (
        stops[stop_cols]
        .merge(
            complaints[["normalized_stop", total_calls_col]],
            on="normalized_stop",
            how="left",
        )
        .merge(
            equity[["normalized_stop", weekly_trips_col]],
            on="normalized_stop",
            how="left",
        )
        .copy()
    )

    rename_map = {
        stops_name_col: "stop_name",
        amenity_gap_col: "amenity_gap",
        total_calls_col: "total_calls",
        weekly_trips_col: "weekly_trips",
    }
    if stops_id_col:
        rename_map[stops_id_col] = "stop_id"
    joined = joined.rename(columns=rename_map)
    joined["total_calls"] = pd.to_numeric(joined["total_calls"], errors="coerce").fillna(0)
    joined["weekly_trips"] = pd.to_numeric(joined["weekly_trips"], errors="coerce").fillna(0)

    coords = build_coordinates_table(stops, cfg, stops_id_col)
    coords = coords.drop_duplicates(subset=[c for c in ["stop_id", "normalized_stop"] if c in coords.columns])

    if "stop_id" in joined.columns and "stop_id" in coords.columns:
        joined = joined.merge(
            coords[["stop_id", "latitude", "longitude"]],
            on="stop_id",
            how="left",
        )
        # Fallback by stop name for any rows with unmatched stop_id.
        by_name = (
            coords[["normalized_stop", "latitude", "longitude"]]
            .dropna(subset=["normalized_stop"])
            .drop_duplicates(subset=["normalized_stop"])
            .set_index("normalized_stop")
        )
        missing = joined["latitude"].isna() | joined["longitude"].isna()
        joined.loc[missing, "latitude"] = joined.loc[missing, "normalized_stop"].map(by_name["latitude"])
        joined.loc[missing, "longitude"] = joined.loc[missing, "normalized_stop"].map(by_name["longitude"])
    else:
        joined = joined.merge(
            coords[["normalized_stop", "latitude", "longitude"]],
            on="normalized_stop",
            how="left",
        )

    council_path = ROOT / cfg["inputs"]["geographies"]["council_districts"]
    tract_path = ROOT / cfg["inputs"]["geographies"]["census_tracts"]

    council_features = load_geojson_features(council_path)
    tract_features = load_geojson_features(tract_path)

    council_key = find_property_key(
        council_features,
        ["District Number", "district_number", "district", "District Name", "name"],
    )
    tract_key = find_property_key(
        tract_features,
        ["geoid", "GEOID", "tractce", "TRACTCE", "name", "namelsad"],
    )

    prepared_council = build_prepared_features(council_features, council_key)
    prepared_tracts = build_prepared_features(tract_features, tract_key)

    def assign_council(row: pd.Series) -> object:
        lat = row.get("latitude")
        lon = row.get("longitude")
        if pd.isna(lat) or pd.isna(lon):
            return np.nan
        return assign_point_to_polygon(Point(float(lon), float(lat)), prepared_council)

    def assign_tract(row: pd.Series) -> object:
        lat = row.get("latitude")
        lon = row.get("longitude")
        if pd.isna(lat) or pd.isna(lon):
            return np.nan
        return assign_point_to_polygon(Point(float(lon), float(lat)), prepared_tracts)

    joined["council_district"] = joined.apply(assign_council, axis=1)
    joined["census_tract"] = joined.apply(assign_tract, axis=1)

    out_stop = ROOT / cfg["outputs"]["stop_geospatial_equity"]
    out_stop.parent.mkdir(parents=True, exist_ok=True)
    joined.to_csv(out_stop, index=False)

    district_summary = (
        joined.groupby("council_district", dropna=False, as_index=False)
        .agg(
            stops=("stop_name", "count"),
            total_calls=("total_calls", "sum"),
            avg_amenity_gap=("amenity_gap", "mean"),
            avg_weekly_trips=("weekly_trips", "mean"),
        )
        .sort_values(["total_calls", "avg_amenity_gap"], ascending=[False, False])
    )
    district_summary.to_csv(ROOT / cfg["outputs"]["district_equity_summary"], index=False)

    tract_summary = (
        joined.groupby("census_tract", dropna=False, as_index=False)
        .agg(
            stops=("stop_name", "count"),
            total_calls=("total_calls", "sum"),
            avg_amenity_gap=("amenity_gap", "mean"),
            avg_weekly_trips=("weekly_trips", "mean"),
        )
        .sort_values(["total_calls", "avg_amenity_gap"], ascending=[False, False])
    )
    tract_summary.to_csv(ROOT / cfg["outputs"]["tract_equity_summary"], index=False)

    print("Geospatial equity scaffold completed.")
    print(
        f"Spatial joins complete. Assigned districts for {joined['council_district'].notna().sum()} stops "
        f"and tracts for {joined['census_tract'].notna().sum()} stops."
    )


if __name__ == "__main__":
    main()
