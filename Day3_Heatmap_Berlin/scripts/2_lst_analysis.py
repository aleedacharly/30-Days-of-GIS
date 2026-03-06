import geopandas as gpd
import rasterio
from rasterstats import zonal_stats
import numpy as np
import pandas as pd


# Load Berlin district boundaries
districts = gpd.read_file('data/raw/berlin_districts.geojson')


# Reproject to match raster CRS (EPSG:25833)
districts = districts.to_crs('EPSG:25833')


# Compute zonal statistics for LST
lst_stats = zonal_stats(
    districts,
    'data/raw/lst_berlin.tif',
    stats=['mean', 'min', 'max', 'std'],
    nodata=-9999
)
# Do the same for NDVI
ndvi_stats = zonal_stats(
    districts,
    'data/raw/ndvi_berlin.tif',
    stats=['mean'],
    nodata=-9999
)


# Add stats to districts GeoDataFrame
districts['lst_mean'] = [s['mean'] for s in lst_stats]
districts['lst_min']  = [s['min']  for s in lst_stats]
districts['lst_max']  = [s['max']  for s in lst_stats]
districts['lst_std']  = [s['std']  for s in lst_stats]
districts['ndvi_mean'] = [s['mean'] for s in ndvi_stats]


# Save processed GeoJSON and CSV
districts.to_file('data/processed/berlin_districts_lst.geojson', driver='GeoJSON')
districts[['name','lst_mean','lst_min','lst_max','ndvi_mean']].to_csv(
    'outputs/uhi_district_stats.csv', index=False)


print(districts[['name','lst_mean','ndvi_mean']].sort_values('lst_mean', ascending=False))

