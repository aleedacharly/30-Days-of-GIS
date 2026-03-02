import geopandas as gpd
import pandas as pd
import osmnx as ox
import warnings
warnings.filterwarnings('ignore')

# ── Load classified data ──────────────────────────────────────────────────────
gdf = gpd.read_file('data/raw/osm_features.geojson')

def classify_landuse(row):
    lu  = str(row.get('landuse',  '')).lower()
    bld = str(row.get('building', '')).lower()
    lei = str(row.get('leisure',  '')).lower()
    nat = str(row.get('natural',  '')).lower()

    if lu in ['residential'] or bld in ['residential','house','apartments','detached']:
        return 'Residential'
    elif lu in ['commercial','retail'] or bld in ['commercial','retail','shop','supermarket']:
        return 'Commercial'
    elif lu in ['industrial','warehouse'] or bld in ['industrial','warehouse']:
        return 'Industrial'
    elif lu in ['park','recreation_ground','grass','forest','orchard'] or \
         lei in ['park','garden','pitch','playground','nature_reserve']:
        return 'Green/Open'
    elif lu in ['railway','highway'] or bld in ['garage','parking']:
        return 'Transport'
    elif lu in ['basin','reservoir'] or nat in ['water']:
        return 'Water'
    else:
        return 'Other'

gdf['landuse_class'] = gdf.apply(classify_landuse, axis=1)
gdf_poly = gdf[gdf.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])].copy()
gdf_proj = gdf_poly.to_crs(epsg=32643)
gdf_proj['area_sqm'] = gdf_proj.geometry.area
gdf_proj.to_file('data/processed/landuse_classified.geojson', driver='GeoJSON')

print("Classification done:")
print(gdf_proj['landuse_class'].value_counts())
print()

# ── Try to fetch real ward polygons (OSM admin_level=10 for Indian wards) ────
print("Attempting to fetch ward boundaries from OSM...")
wards = None

try:
    # Indian municipal wards are typically admin_level=10
    result = ox.features_from_place(
        'Kozhikode Municipal Corporation, Kerala, India',
        tags={'boundary': 'administrative', 'admin_level': '10'}
    )
    result = result[result.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])]

    if len(result) > 3:
        wards = result[['geometry', 'name']].copy()
        wards = wards.to_crs(epsg=32643)
        print(f"Found {len(wards)} ward polygons from OSM.")
    else:
        print("Too few ward polygons found at admin_level=10.")
except Exception as e:
    print(f"Ward fetch failed: {e}")

# ── Spatial join (only if we have real wards) ─────────────────────────────────
if wards is not None and len(wards) > 3:
    joined = gpd.sjoin(gdf_proj, wards[['geometry', 'name']], how='left', predicate='within')
    joined['zone'] = joined['name'].fillna('Unknown')
else:
    # No ward polygons — assign everything to one city-level zone
    joined = gdf_proj.copy()
    joined['zone'] = 'Kozhikode City'

# ── Summary statistics ────────────────────────────────────────────────────────
summary = (
    joined
    .groupby(['zone', 'landuse_class'])['area_sqm']
    .sum()
    .reset_index()
)
summary.columns = ['zone', 'landuse_class', 'area_sqm']
summary['area_ha'] = (summary['area_sqm'] / 10000).round(2)

zone_total = summary.groupby('zone')['area_sqm'].sum().rename('zone_total')
summary = summary.join(zone_total, on='zone')
summary['pct_share'] = (summary['area_sqm'] / summary['zone_total'] * 100).round(2)
summary = summary.drop(columns='zone_total')

summary.to_csv('outputs/landuse_summary.csv', index=False)
print("\nSummary CSV saved to outputs/landuse_summary.csv")
print(summary.to_string(index=False))