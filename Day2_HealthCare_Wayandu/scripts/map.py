import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import contextily as ctx
import pandas as pd


# Load layers
villages = gpd.read_file('data/processed/villages_classified.geojson')
roads = gpd.read_file('data/processed/wayanad_roads.geojson')
iso_15 = gpd.read_file('data/processed/isochrone_15min.geojson')
iso_30 = gpd.read_file('data/processed/isochrone_30min.geojson')
phc = gpd.read_file('data/raw/wayanad_phc.geojson')


# Reproject all to Web Mercator for contextily basemap
crs = 'EPSG:3857'
villages = villages.to_crs(crs)
roads = roads.to_crs(crs)
iso_15 = iso_15.to_crs(crs)
iso_30 = iso_30.to_crs(crs)
phc = phc.to_crs(crs)

# ─── MAP ─────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 10))
ax = axes[0]


# Draw isochrones
iso_30.plot(ax=ax, color='#FFCC00', alpha=0.35, label='Within 30 min')
iso_15.plot(ax=ax, color='#00AA44', alpha=0.45, label='Within 15 min')


# Draw roads
roads.plot(ax=ax, linewidth=0.3, color='#666666', alpha=0.4)


# Colour-coded village points
colour_map = {
    'Within 15 min': '#006400',
    '15-30 min': '#FFA500',
    'Beyond 30 min (Underserved)': '#CC0000'
}
for zone, colour in colour_map.items():
    subset = villages[villages['access_zone'] == zone]
    subset.plot(ax=ax, color=colour, markersize=5, label=zone, zorder=5)


# PHC markers
phc.plot(ax=ax, color='blue', marker='+', markersize=80, zorder=10, label='PHC')


# Add basemap
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, zoom=10)


# Legend and labels
ax.set_title('Healthcare Access Zones\nWayanad District, Kerala', fontsize=14, fontweight='bold')
ax.legend(loc='lower left', fontsize=9)
ax.set_axis_off()


# ─── BAR CHART ───────────────────────────────────────
ax2 = axes[1]
summary = pd.read_csv('outputs/access_zone_summary.csv')
colours = ['#006400', '#FFA500', '#CC0000']
bars = ax2.bar(summary['access_zone'], summary['pct'], color=colours, edgecolor='white')


for bar, val in zip(bars, summary['pct']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f'{val:.1f}%', ha='center', fontsize=11, fontweight='bold')


ax2.set_title('% Population by Healthcare Access Zone\nWayanad District', fontsize=13, fontweight='bold')
ax2.set_ylabel('% of Total Population', fontsize=11)
ax2.set_xlabel('Access Zone', fontsize=11)
ax2.set_ylim(0, 100)
ax2.tick_params(axis='x', labelsize=9)


plt.tight_layout()
plt.savefig('outputs/access_map.png', dpi=300, bbox_inches='tight')
print('Map saved to outputs/access_map.png')
plt.show()
