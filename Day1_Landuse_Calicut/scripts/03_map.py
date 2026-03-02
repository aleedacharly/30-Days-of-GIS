import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import contextily as ctx
import pandas as pd
import numpy as np
from shapely.geometry import Point, box
from shapely.ops import unary_union
from matplotlib.patches import PathPatch
from matplotlib.path import Path

# ── Load data ─────────────────────────────────────────────────────────────────
gdf = gpd.read_file('data/processed/landuse_classified.geojson')
gdf_wgs = gdf.to_crs(epsg=4326)

city = gpd.read_file('data/raw/kozhikode_boundary.geojson')
city_wgs = city.to_crs(epsg=4326)
gdf_wgs = gpd.clip(gdf_wgs, city_wgs)

gdf_plot = gdf_wgs[gdf_wgs['landuse_class'] != 'Other'].copy()
print("Features being plotted:")
print(gdf_plot['landuse_class'].value_counts())

# ── Color palette ─────────────────────────────────────────────────────────────
color_map = {
    'Residential': '#E07B39',
    'Commercial':  '#C0392B',
    'Industrial':  '#7F8C8D',
    'Green/Open':  '#27AE60',
    'Transport':   '#2980B9',
    'Water':       '#85C1E9',
}

# ── Main figure ───────────────────────────────────────────────────────────────
fig, ax = plt.subplots(1, 1, figsize=(13, 15))

minx, miny, maxx, maxy = city_wgs.total_bounds
pad = 0.02
ax.set_xlim(minx - pad, maxx + pad)
ax.set_ylim(miny - pad, maxy + pad)

# ── 1. Basemap ────────────────────────────────────────────────────────────────
ctx.add_basemap(
    ax,
    crs=gdf_wgs.crs.to_string(),
    source=ctx.providers.CartoDB.PositronNoLabels,
    alpha=0.6,
    zorder=1
)

# ── 2. White mask outside city boundary ──────────────────────────────────────
def polygon_to_patch(geom, **kwargs):
    if geom.geom_type == 'MultiPolygon':
        paths = []
        for poly in geom.geoms:
            ext = np.array(poly.exterior.coords)
            codes = [Path.MOVETO] + [Path.LINETO]*(len(ext)-2) + [Path.CLOSEPOLY]
            paths.append(Path(ext, codes))
            for interior in poly.interiors:
                ic = np.array(interior.coords)
                codes = [Path.MOVETO] + [Path.LINETO]*(len(ic)-2) + [Path.CLOSEPOLY]
                paths.append(Path(ic, codes))
        return PathPatch(Path.make_compound_path(*paths), **kwargs)
    else:
        ext = np.array(geom.exterior.coords)
        codes = [Path.MOVETO] + [Path.LINETO]*(len(ext)-2) + [Path.CLOSEPOLY]
        return PathPatch(Path(ext, codes), **kwargs)

big_box = box(minx - pad, miny - pad, maxx + pad, maxy + pad)
city_union = unary_union(city_wgs.geometry)
mask_geom = big_box.difference(city_union)
ax.add_patch(polygon_to_patch(
    mask_geom, facecolor='white', edgecolor='none', zorder=2, linewidth=0
))

# ── 3. City boundary ──────────────────────────────────────────────────────────
city_wgs.boundary.plot(ax=ax, color='#2C3E50', linewidth=1.5, linestyle='--', zorder=3)

# ── 4. Land use features ──────────────────────────────────────────────────────
layer_order = ['Water', 'Green/Open', 'Transport', 'Industrial', 'Commercial', 'Residential']
for i, cat in enumerate(layer_order):
    subset = gdf_plot[gdf_plot['landuse_class'] == cat]
    if len(subset) == 0:
        continue
    subset.plot(ax=ax, color=color_map[cat], alpha=0.85,
                linewidth=0.2, edgecolor='white', zorder=4+i)

# ── 5. Place labels ───────────────────────────────────────────────────────────
known_places = pd.DataFrame({
    'name': [
        'Palayam', 'Mananchira', 'Calicut Beach', 'Nadakkavu',
        'Arayidathupalam', 'Mavoor Road', 'Medical College',
        'Chevayur', 'Thondayad', 'West Hill', 'Elathur',
        'Beypore', 'Feroke', 'Kunnamangalam'
    ],
    'lon': [
        75.7804, 75.7762, 75.7721, 75.7880,
        75.7950, 75.8020, 75.8033,
        75.8100, 75.8180, 75.7950, 75.8300,
        75.8133, 75.8350, 75.8450
    ],
    'lat': [
        11.2588, 11.2530, 11.2490, 11.2650,
        11.2700, 11.2750, 11.2620,
        11.2830, 11.2950, 11.2700, 11.3100,
        11.1733, 11.1580, 11.2350
    ],
    'dx': [-40, -45, -50,  30,  35,  40,  45,  35,  20, -40,  20, -30,  30,  40],
    'dy': [-15, -25, -35,  15,  20,  30, -15,  20,  25,  20,  30, -20, -20,  20]
})

geometry = [Point(xy) for xy in zip(known_places.lon, known_places.lat)]
places_wgs = gpd.GeoDataFrame(known_places, geometry=geometry, crs='EPSG:4326')

for idx, row in places_wgs.iterrows():
    x, y = row.geometry.x, row.geometry.y
    ax.plot(x, y, 'o', color='#2C3E50', markersize=4, zorder=11)
    ax.annotate(
        row['name'], xy=(x, y),
        xytext=(row['dx'], row['dy']),
        textcoords='offset points',
        fontsize=8.5, fontweight='bold', color='#1A1A2E',
        ha='center', va='center',
        arrowprops=dict(arrowstyle='-', color='#555555',
                        linewidth=0.8, shrinkA=0, shrinkB=3),
        path_effects=[pe.withStroke(linewidth=2.5, foreground='white')],
        zorder=12
    )

# ── 6. India inset map ────────────────────────────────────────────────────────
ax_inset = inset_axes(ax, width="22%", height="22%", loc='upper right',
                      bbox_to_anchor=ax.bbox, bbox_transform=ax.transAxes)

try:
    # Download India boundary from Natural Earth via geopandas datasets
    import geodatasets
    world = gpd.read_file(geodatasets.get_path('naturalearth.land'))
    india = world[world.geometry.intersects(
        box(68, 6, 98, 38)
    )].copy()
    india.plot(ax=ax_inset, color='#F0F0F0', edgecolor='#AAAAAA', linewidth=0.5)
except Exception:
    # Fallback — download directly
    try:
        url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
        world = gpd.read_file(url)
        india = world[world['ADMIN'] == 'India']
        india.plot(ax=ax_inset, color='#F0F0F0', edgecolor='#AAAAAA', linewidth=0.5)
    except Exception:
        # Final fallback — just draw a box
        ax_inset.set_facecolor('#E8F4F8')

# Plot Kozhikode marker on inset
ax_inset.plot(75.78, 11.25, 'o', color='#C0392B', markersize=6, zorder=5)
ax_inset.plot(75.78, 11.25, 'o', color='white', markersize=3, zorder=6)

# Zoom inset to India extent
ax_inset.set_xlim(68, 98)
ax_inset.set_ylim(6, 38)
ax_inset.set_aspect('equal')
ax_inset.set_xticks([])
ax_inset.set_yticks([])
ax_inset.set_facecolor('#D6EAF8')  # light blue sea colour
for spine in ax_inset.spines.values():
    spine.set_edgecolor('#AAAAAA')
    spine.set_linewidth(0.8)

# Label
ax_inset.text(0.5, -0.06, 'Location in India',
              transform=ax_inset.transAxes,
              ha='center', fontsize=7, color='#555555', style='italic')

# ── Legend ────────────────────────────────────────────────────────────────────
patches = [mpatches.Patch(color=c, label=l) for l, c in color_map.items()]
patches.append(mpatches.Patch(
    facecolor='none', edgecolor='#2C3E50',
    linestyle='--', linewidth=1.5, label='City Boundary'
))
ax.legend(handles=patches, loc='lower left', fontsize=11,
          title='Land Use Category', title_fontsize=12,
          framealpha=0.95, edgecolor='#CCCCCC', fancybox=True)

# ── Title & north arrow ───────────────────────────────────────────────────────
ax.set_title(
    'Urban Land Use Map — Kozhikode Municipal Corporation\n'
    'Source: OpenStreetMap | Unclassified features excluded',
    fontsize=15, fontweight='bold', pad=20, color='#2C3E50'
)
ax.text(
    0.99, 0.01,
    'N ↑\nProjection: WGS84\nData: © OSM contributors',
    transform=ax.transAxes, ha='right', va='bottom', fontsize=9,
    style='italic', color='#555555',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7)
)

ax.set_axis_off()
plt.tight_layout()
plt.savefig('outputs/landuse_map.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
print("Map saved!")