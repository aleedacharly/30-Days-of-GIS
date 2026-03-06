import geopandas as gpd
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


# Load data
districts = gpd.read_file('data/processed/berlin_districts_lst.geojson')


fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.suptitle('Urban Heat Island — Berlin, Summer 2021', fontsize=16, fontweight='bold')


# --- LEFT PANEL: LST Raster Map ---
ax1 = axes[0]
with rasterio.open('data/raw/lst_berlin.tif') as src:
    lst_data = src.read(1)
    lst_data = np.where(lst_data < -50, np.nan, lst_data)  # mask nodata
    extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
im = ax1.imshow(lst_data, cmap='RdBu_r', vmin=20, vmax=45,
               extent=extent, origin='upper', aspect='auto')
districts.boundary.plot(ax=ax1, color='white', linewidth=0.8, alpha=0.7)


# Annotate district names
for _, row in districts.iterrows():
    ax1.annotate(row['name'].split('-')[0],  # shorten long names
                xy=(row.geometry.centroid.x, row.geometry.centroid.y),
                fontsize=6, ha='center', color='white', fontweight='bold')


plt.colorbar(im, ax=ax1, label='Land Surface Temperature (°C)', shrink=0.8)
ax1.set_title('LST Raster with Bezirk Boundaries', fontweight='bold')
ax1.set_xlabel('Easting (m, UTM 33N)')
ax1.set_ylabel('Northing (m, UTM 33N)')


# --- RIGHT PANEL: Bar Chart of Mean LST per District ---
ax2 = axes[1]
sorted_d = districts.sort_values('lst_mean', ascending=True)
colours = plt.cm.RdBu_r(
    (sorted_d['lst_mean'] - sorted_d['lst_mean'].min()) /
    (sorted_d['lst_mean'].max() - sorted_d['lst_mean'].min())
)
ax2.barh(sorted_d['name'], sorted_d['lst_mean'], color=colours)
ax2.set_xlabel('Mean LST (°C)')
ax2.set_title('Mean LST per District — Hottest to Coolest', fontweight='bold')
ax2.axvline(districts['lst_mean'].mean(), color='black', linestyle='--', label='City Mean')
ax2.legend()


plt.tight_layout()
plt.savefig('outputs/lst_map.png', dpi=300, bbox_inches='tight')
print('Saved: outputs/lst_map.png')
