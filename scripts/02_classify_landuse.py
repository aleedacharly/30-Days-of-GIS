import geopandas as gpd
import pandas as pd
import osmnx as ox


gdf = gpd.read_file('data/raw/osm_features.geojson')

def classify_landuse(row):
    lu = str(row.get('landuse', '')).lower()
    bld = str(row.get('building', '')).lower()
    lei = str(row.get('leisure', '')).lower()
    nat = str(row.get('natural', '')).lower()

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

# Keep only polygon geometries for area calculation
gdf_poly = gdf[gdf.geometry.geom_type.isin(['Polygon','MultiPolygon'])].copy()

# Reproject to metric CRS (UTM Zone 43N for Kerala)
gdf_proj = gdf_poly.to_crs(epsg=32643)
gdf_proj['area_sqm'] = gdf_proj.geometry.area

# Save classified output
gdf_proj.to_file('data/processed/landuse_classified.geojson', driver='GeoJSON')
print('Classification complete!')
print(gdf_proj['landuse_class'].value_counts())


# Get ward boundaries (OSM admin_level=8 for municipality wards)
wards = ox.geocode_to_gdf('Kozhikode Municipal Corporation, Kerala', which_result=None)
# If wards not available, use city boundary as fallback:
# wards = gpd.read_file('data/raw/kozhikode_boundary.geojson')

wards = wards.to_crs(epsg=32643)
gdf_proj = gpd.read_file('data/processed/landuse_classified.geojson')

# Spatial join: assign ward to each polygon
joined = gpd.sjoin(gdf_proj, wards[['geometry','name']], how='left', predicate='within')

# Summary statistics: area per class per ward
summary = joined.groupby(['name','landuse_class'])['area_sqm'].sum().reset_index()
summary.columns = ['ward', 'landuse_class', 'area_sqm']
summary['area_ha'] = summary['area_sqm'] / 10000

# Calculate percentage share per ward
ward_total = summary.groupby('ward')['area_sqm'].sum().rename('ward_total')
summary = summary.join(ward_total, on='ward')
summary['pct_share'] = (summary['area_sqm'] / summary['ward_total'] * 100).round(2)

summary.to_csv('outputs/landuse_summary.csv', index=False)
print('Summary CSV saved!')
print(summary.head(10))
