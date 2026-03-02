import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import warnings
warnings.filterwarnings('ignore')

# ── Define KMC boundary (land only — no sea on west) ─────────────────────────
# Coastline runs roughly at lon 75.737 for Kozhikode
# Western edge follows the coast, not extending into the sea

kozhikode_kmc_coords = [
    (75.7370, 11.1600),   # SW coast — Ramanattukara
    (75.7600, 11.1500),   # South
    (75.8200, 11.1700),   # Feroke east
    (75.8500, 11.1900),   # East boundary south
    (75.8700, 11.2300),   # East boundary mid
    (75.8600, 11.2700),   # Kunnamangalam area
    (75.8500, 11.3100),   # Elathur east
    (75.8200, 11.3400),   # North east
    (75.7900, 11.3500),   # North
    (75.7600, 11.3400),   # North west
    (75.7400, 11.3200),   # West north — coast
    (75.7370, 11.2900),   # Coast mid-north
    (75.7370, 11.2600),   # Coast — Calicut Beach area
    (75.7370, 11.2300),   # Coast mid-south
    (75.7370, 11.1900),   # Coast south
    (75.7370, 11.1600),   # back to SW start
]

kmc_polygon = Polygon(kozhikode_kmc_coords)
city = gpd.GeoDataFrame(
    {'name': ['Kozhikode Municipal Corporation']},
    geometry=[kmc_polygon],
    crs='EPSG:4326'
)

area_km2 = city.to_crs(epsg=32643).geometry.area.sum() / 1e6
print(f"KMC boundary area: {area_km2:.1f} km²")
city.to_file('data/raw/kozhikode_boundary.geojson', driver='GeoJSON')
print("Boundary saved.")

# ── Fetch OSM features ────────────────────────────────────────────────────────
print("\nFetching OSM features...")
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