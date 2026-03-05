import osmnx as ox
import geopandas as gpd

# Download Berlin political boundary
berlin = ox.geocode_to_gdf('Berlin, Germany')

# Reproject to WGS84 (required for GEE upload)
berlin = berlin.to_crs('EPSG:4326')

# Save as shapefile
berlin.to_file('data/raw/berlin_boundary.shp')
print('Saved shapefile files in data/raw/')