import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon
import warnings
warnings.filterwarnings('ignore')

# ── Manually define Kozhikode Municipal Corporation boundary ──────────────────
# OSM does not have the KMC boundary as a polygon.
# These coordinates trace the actual ~118 km² municipal area.
# Source: approximated from KMC ward map and GADM Level 3 data.

kozhikode_kmc_coords = [
    (75.7200, 11.1600),   # SW — Feroke/Ramanattukara south
    (75.7600, 11.1500),   # SE bottom
    (75.8200, 11.1700),   # Feroke east
    (75.8500, 11.1900),   # East boundary south
    (75.8700, 11.2300),   # East boundary mid
    (75.8600, 11.2700),   # Kunnamangalam area
    (75.8500, 11.3100),   # Elathur east
    (75.8200, 11.3400),   # North east
    (75.7900, 11.3500),   # North
    (75.7600, 11.3400),   # North west
    (75.7400, 11.3200),   # West north
    (75.7250, 11.2800),   # West mid — coastal area
    (75.7150, 11.2400),   # West — Calicut Beach area
    (75.7100, 11.2000),   # SW coast
    (75.7200, 11.1600),   # back to start
]

kmc_polygon = Polygon(kozhikode_kmc_coords)
city = gpd.GeoDataFrame(
    {'name': ['Kozhikode Municipal Corporation']},
    geometry=[kmc_polygon],
    crs='EPSG:4326'
)

area_km2 = city.to_crs(epsg=32643).geometry.area.sum() / 1e6
print(f"Manual KMC boundary area: {area_km2:.1f} km²")
print(f"Bounds: {city.total_bounds.round(4)}")

# Save boundary
city.to_file('data/raw/kozhikode_boundary.geojson', driver='GeoJSON')
print("Boundary saved to data/raw/kozhikode_boundary.geojson")

# ── Fetch OSM features within this boundary ───────────────────────────────────
print("\nFetching OSM features...")

# Use the polygon directly instead of a place name string
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

import pandas as pd
if all_features:
    combined = pd.concat(all_features)
    combined.to_file('data/raw/osm_features.geojson', driver='GeoJSON')
    print(f"\nTotal features saved: {len(combined)}")
else:
    print("No features fetched — check internet connection")