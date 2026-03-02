import geopandas as gpd
import pandas as pd

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
