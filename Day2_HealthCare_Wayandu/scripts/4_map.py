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
phc = gpd.read_file('data/raw/wayanad_phc_corrected.geojson')

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

# Draw isochrones — 30 min first (bottom), then 15 min on top
iso_30.plot(ax=ax, color='#FFCC00', alpha=0.45, label='_nolegend_')
iso_15.plot(ax=ax, color='#00AA44', alpha=0.55, label='_nolegend_')

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
phc.plot(ax=ax, color='blue', marker='+', markersize=80, zorder=10, label='PHC Location')

# Add basemap
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, zoom=10)

# ── Custom legend with isochrone colour explanation ──
legend_handles = [
    mpatches.Patch(color='#00AA44', alpha=0.7,
                   label='Green zone — Within 15 min drive of a PHC'),
    mpatches.Patch(color='#FFCC00', alpha=0.7,
                   label='Yellow zone — 15 to 30 min drive of a PHC\n(only the outer yellow ring, not the green area)'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#006400',
               markersize=7, label='Village — Within 15 min'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFA500',
               markersize=7, label='Village — 15 to 30 min'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#CC0000',
               markersize=7, label='Village — Beyond 30 min (Underserved)'),
    plt.Line2D([0], [0], marker='+', color='blue', markersize=10,
               linewidth=0, label='PHC Location'),
]
ax.legend(handles=legend_handles, loc='lower left', fontsize=8,
          framealpha=0.9, title='Legend', title_fontsize=9)

ax.set_title('Healthcare Access Zones\nWayanad District, Kerala', fontsize=14, fontweight='bold')
ax.set_axis_off()

# ─── BAR CHART ───────────────────────────────────────
ax2 = axes[1]
summary = pd.read_csv('outputs/access_zone_summary.csv')

# Force correct order: Within 15 min → 15-30 min → Beyond 30 min
order = ['Within 15 min', '15-30 min', 'Beyond 30 min (Underserved)']
summary['access_zone'] = pd.Categorical(summary['access_zone'], categories=order, ordered=True)
summary = summary.sort_values('access_zone')

# Match bar colours to map colours
bar_colours = ['#006400', '#FFA500', '#CC0000']
bars = ax2.bar(summary['access_zone'], summary['pct'], color=bar_colours, edgecolor='white', width=0.5)

for bar, val in zip(bars, summary['pct']):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
             f'{val:.1f}%', ha='center', fontsize=11, fontweight='bold')

# X-axis labels — cleaner readable names
ax2.set_xticks(range(len(order)))
ax2.set_xticklabels([
    'Within 15 min\n(Good Access)',
    '15–30 min\n(Moderate Access)',
    'Beyond 30 min\n(Underserved)'
], fontsize=10)

ax2.set_title('% Population by Healthcare Access Zone\nWayanad District', fontsize=13, fontweight='bold')
ax2.set_ylabel('% of Total Population', fontsize=11)
ax2.set_xlabel('Access Zone', fontsize=11)
ax2.set_ylim(0, 100)

# Add a note explaining the zones
ax2.text(0.5, -0.18,
         'Zones based on car drive-time isochrones from nearest government PHC.\n'
         'Green = reachable within 15 min | Yellow ring = 15–30 min band | Red = beyond 30 min.',
         transform=ax2.transAxes, ha='center', fontsize=8, color='#444444',
         wrap=True)

plt.tight_layout()
plt.savefig('outputs/access_map.png', dpi=300, bbox_inches='tight')
print('Map saved to outputs/access_map.png')
plt.show()