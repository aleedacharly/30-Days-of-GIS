import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
import numpy as np
import pandas as pd

districts = gpd.read_file('data/raw/berlin_districts.geojson')
districts = districts.to_crs('EPSG:25833')

results = []

for _, row in districts.iterrows():
    geom = [mapping(row.geometry)]
    
    with rasterio.open('data/raw/lst_berlin.tif') as src:
        try:
            lst_masked, _ = mask(src, geom, crop=True)
            vals = lst_masked.flatten()
            # Filter out physically unrealistic values
            # Berlin in June: nothing below 15°C or above 55°C is real LST
            vals = vals[(vals > 15) & (vals < 55)]
        except:
            vals = np.array([])
    
    with rasterio.open('data/raw/ndvi_berlin.tif') as src:
        try:
            ndvi_masked, _ = mask(src, geom, crop=True)
            ndvi_vals = ndvi_masked.flatten()
            ndvi_vals = ndvi_vals[(ndvi_vals > -1) & (ndvi_vals < 1) & (ndvi_vals != 0)]
        except:
            ndvi_vals = np.array([])
    
    results.append({
        'name': row['name'],
        'lst_mean':  round(np.mean(vals), 2)  if len(vals) > 0 else np.nan,
        'lst_min':   round(np.min(vals), 2)   if len(vals) > 0 else np.nan,
        'lst_max':   round(np.max(vals), 2)   if len(vals) > 0 else np.nan,
        'lst_std':   round(np.std(vals), 2)   if len(vals) > 0 else np.nan,
        'ndvi_mean': round(np.mean(ndvi_vals), 3) if len(ndvi_vals) > 0 else np.nan,
        'pixel_count': len(vals)
    })

df = pd.DataFrame(results)
print(df.sort_values('lst_mean', ascending=False).to_string())

df.to_csv('outputs/uhi_district_stats.csv', index=False)
print('\nSaved!')