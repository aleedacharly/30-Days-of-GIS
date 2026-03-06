import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load districts and reproject
districts = gpd.read_file('data/raw/berlin_districts.geojson')
districts = districts.to_crs('EPSG:25833')

# Recalculate correct stats
results = []
for _, row in districts.iterrows():
    geom = [mapping(row.geometry)]
    with rasterio.open('data/raw/lst_berlin.tif') as src:
        out, _ = mask(src, geom, crop=True)
        vals = out.flatten()
        vals = vals[(vals > 15) & (vals < 55)]
    with rasterio.open('data/raw/ndvi_berlin.tif') as src:
        out2, _ = mask(src, geom, crop=True)
        ndvi_vals = out2.flatten()
        ndvi_vals = ndvi_vals[(ndvi_vals > -1) & (ndvi_vals < 1) & (ndvi_vals != 0)]
    results.append({
        'name':      row['name'],
        'lst_mean':  round(np.mean(vals), 2)      if len(vals) > 0 else np.nan,
        'lst_min':   round(np.min(vals), 2)       if len(vals) > 0 else np.nan,
        'lst_max':   round(np.max(vals), 2)       if len(vals) > 0 else np.nan,
        'lst_std':   round(np.std(vals), 2)       if len(vals) > 0 else np.nan,
        'ndvi_mean': round(np.mean(ndvi_vals), 3) if len(ndvi_vals) > 0 else np.nan,
    })

df = pd.DataFrame(results)
df.to_csv('outputs/uhi_district_stats.csv', index=False)
print('CSV saved. Neukölln:', df[df['name']=='Neukölln']['lst_mean'].values[0])

# Merge stats into geodataframe
districts = districts.merge(df, on='name')

# ---- LST Map + Bar Chart ----
fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.suptitle('Urban Heat Island — Berlin, Summer 2020', fontsize=16, fontweight='bold')

# Left panel — LST raster
ax1 = axes[0]
with rasterio.open('data/raw/lst_berlin.tif') as src:
    lst_data = src.read(1)
    lst_data = np.where((lst_data < 15) | (lst_data > 55), np.nan, lst_data)
    extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]

im = ax1.imshow(lst_data, cmap='RdBu_r', vmin=20, vmax=45,
               extent=extent, origin='upper', aspect='auto')
districts.boundary.plot(ax=ax1, color='white', linewidth=0.8, alpha=0.7)
for _, row in districts.iterrows():
    ax1.annotate(row['name'].split('-')[0],
                xy=(row.geometry.centroid.x, row.geometry.centroid.y),
                fontsize=6, ha='center', color='white', fontweight='bold')
plt.colorbar(im, ax=ax1, label='Land Surface Temperature (°C)', shrink=0.8)
ax1.set_title('LST Raster with Bezirk Boundaries', fontweight='bold')
ax1.set_xlabel('Easting (m, UTM 33N)')
ax1.set_ylabel('Northing (m, UTM 33N)')

# Right panel — bar chart
ax2 = axes[1]
sorted_d = districts.sort_values('lst_mean', ascending=True)
colours = plt.cm.RdBu_r(
    (sorted_d['lst_mean'] - sorted_d['lst_mean'].min()) /
    (sorted_d['lst_mean'].max() - sorted_d['lst_mean'].min())
)
ax2.barh(sorted_d['name'], sorted_d['lst_mean'], color=colours)
ax2.set_xlabel('Mean LST (°C)')
ax2.set_title('Mean LST per District — Hottest to Coolest', fontweight='bold')
ax2.axvline(districts['lst_mean'].mean(), color='black',
            linestyle='--', label=f'City Mean ({districts["lst_mean"].mean():.1f}°C)')
ax2.legend()

plt.tight_layout()
plt.savefig('outputs/lst_map.png', dpi=300, bbox_inches='tight')
print('Saved: outputs/lst_map.png')