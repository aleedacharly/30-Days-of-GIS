import geopandas as gpd
import rasterio
import numpy as np

districts = gpd.read_file('data/raw/berlin_districts.geojson')
districts = districts.to_crs('EPSG:25833')

# Check geometry validity
print(districts[['name', 'geometry']].copy().assign(
    is_valid=districts.geometry.is_valid,
    geom_type=districts.geometry.type,
    area_km2=districts.geometry.area / 1e6
))

# Check raster extent vs districts extent
with rasterio.open('data/raw/lst_berlin.tif') as src:
    raster_bounds = src.bounds
    print('\nRaster bounds:', raster_bounds)
    
print('\nDistricts bounds:', districts.total_bounds)

# Check if each district overlaps with raster
from shapely.geometry import box
raster_box = box(raster_bounds.left, raster_bounds.bottom, 
                 raster_bounds.right, raster_bounds.top)

for _, row in districts.iterrows():
    overlaps = row.geometry.intersects(raster_box)
    print(f"{row['name']}: overlaps raster = {overlaps}")