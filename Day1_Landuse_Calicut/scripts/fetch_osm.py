import osmnx as ox
import os
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import warnings
warnings.filterwarnings('ignore')

# ── Step 1: Define broad KMC envelope (intentionally includes sea) ────────────
kozhikode_kmc_coords = [
    (75.7000, 11.1600),   # SW — extends into sea
    (75.7600, 11.1500),
    (75.8200, 11.1700),
    (75.8500, 11.1900),
    (75.8700, 11.2300),
    (75.8600, 11.2700),
    (75.8500, 11.3100),
    (75.8200, 11.3400),
    (75.7900, 11.3500),
    (75.7600, 11.3400),
    (75.7400, 11.3200),
    (75.7000, 11.2900),
    (75.7000, 11.2600),
    (75.7000, 11.2300),
    (75.7000, 11.1900),
    (75.7000, 11.1600),
]
kmc_polygon = Polygon(kozhikode_kmc_coords)

# ── Step 2: Get land geometry from Natural Earth to clip away the sea ─────────
print("Fetching land mask to clip coastline...")
try:
    import geodatasets
    land = gpd.read_file(geodatasets.get_path('naturalearth.land'))
    land_wgs = land.to_crs(epsg=4326)
    # Clip to India region only for speed
    india_box = box(74, 10, 77, 13)
    land_local = land_wgs.clip(india_box)
    land_union = unary_union(land_local.geometry)
    # Clip the KMC polygon to land only — removes sea
    kmc_land_only = kmc_polygon.intersection(land_union)
    print(f"Coastline clip successful.")
except Exception as e:
    print(f"Land mask failed ({e}), using manual coastal trim instead.")
    # Manual fallback: shift western edge to ~coastline longitude
    kozhikode_kmc_coords_land = [
        (75.7380, 11.1600),
        (75.7600, 11.1500),
        (75.8200, 11.1700),
        (75.8500, 11.1900),
        (75.8700, 11.2300),
        (75.8600, 11.2700),
        (75.8500, 11.3100),
        (75.8200, 11.3400),
        (75.7900, 11.3500),
        (75.7600, 11.3400),
        (75.7400, 11.3200),
        (75.7380, 11.2900),
        (75.7380, 11.2600),
        (75.7380, 11.2300),
        (75.7380, 11.1900),
        (75.7380, 11.1600),
    ]
    kmc_land_only = Polygon(kozhikode_kmc_coords_land)

# ── Step 3: Save the land-only boundary ──────────────────────────────────────
city = gpd.GeoDataFrame(
    {'name': ['Kozhikode Municipal Corporation']},
    geometry=[kmc_land_only],
    crs='EPSG:4326'
)
area_km2 = city.to_crs(epsg=32643).geometry.area.sum() / 1e6
print(f"Final KMC boundary area: {area_km2:.1f} km²")
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('outputs', exist_ok=True)
city.to_file('data/raw/kozhikode_boundary.geojson', driver='GeoJSON')
print("Boundary saved to data/raw/kozhikode_boundary.geojson")

# ── Step 4: Fetch OSM features ────────────────────────────────────────────────
print("\nFetching OSM features within boundary...")
polygon = city.geometry.iloc[0]

tags_list = [
    {'landuse': True},
    {'building': True},
    {'leisure': True},
    {'natural': ['water', 'wood', 'grassland']},
]

all_features = []
for tags in tags_list:
    try:
        features = ox.features_from_polygon(polygon, tags=tags)
        all_features.append(features)
        print(f"  {list(tags.keys())[0]}: {len(features)} features")
    except Exception as e:
        print(f"  {list(tags.keys())[0]}: failed — {e}")

if all_features:
    combined = pd.concat(all_features)
    combined.to_file('data/raw/osm_features.geojson', driver='GeoJSON')
    print(f"\nTotal features saved: {len(combined)}")
else:
    print("No features fetched.")