import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import contextily as ctx
import osmnx as ox
import pandas as pd
import matplotlib.patheffects as pe
from shapely.geometry import Point, box
from shapely.ops import unary_union
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np

# ── Load data ─────────────────────────────────────────────────────────────────
gdf = gpd.read_file('data/processed/landuse_classified.geojson')
gdf_wgs = gdf.to_crs(epsg=4326)

# ── Clip to actual Municipal Corporation boundary ─────────────────────────────
city = gpd.read_file('data/raw/kozhikode_boundary.geojson')
gdf_wgs = gpd.clip(gdf_wgs, city)

# ── Drop "Other" — adds noise, not information ────────────────────────────────
gdf_plot = gdf_wgs[gdf_wgs['landuse_class'] != 'Other'].copy()

print("Features being plotted (excluding Other):")
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

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(1, 1, figsize=(13, 15))

layer_order = ['Water', 'Green/Open', 'Transport', 'Industrial', 'Commercial', 'Residential']

for cat in layer_order:
    subset = gdf_plot[gdf_plot['landuse_class'] == cat]
    if len(subset) == 0:
        continue
    subset.plot(
        ax=ax,
        color=color_map[cat],
        alpha=0.85,
        linewidth=0.2,
        edgecolor='white'
    )

# ── Basemap (add before mask so mask sits on top) ─────────────────────────────
city_wgs = city.to_crs(epsg=4326)

ctx.add_basemap(
    ax,
    crs=gdf_wgs.crs.to_string(),
    source=ctx.providers.CartoDB.PositronNoLabels,
    alpha=0.6
)

# ── Mask everything outside city boundary ─────────────────────────────────────
def polygon_to_patch(geom, **kwargs):
    """Convert a shapely polygon/multipolygon to a matplotlib PathPatch."""
    if geom.geom_type == 'MultiPolygon':
        paths = []
        for poly in geom.geoms:
            exterior = np.array(poly.exterior.coords)
            codes = ([Path.MOVETO] +
                     [Path.LINETO] * (len(exterior) - 2) +
                     [Path.CLOSEPOLY])
            paths.append(Path(exterior, codes))
            for interior in poly.interiors:
                interior_coords = np.array(interior.coords)
                codes = ([Path.MOVETO] +
                         [Path.LINETO] * (len(interior_coords) - 2) +
                         [Path.CLOSEPOLY])
                paths.append(Path(interior_coords, codes))
        combined = Path.make_compound_path(*paths)
        return PathPatch(combined, **kwargs)
    else:
        exterior = np.array(geom.exterior.coords)
        codes = ([Path.MOVETO] +
                 [Path.LINETO] * (len(exterior) - 2) +
                 [Path.CLOSEPOLY])
        path = Path(exterior, codes)
        return PathPatch(path, **kwargs)

minx, miny, maxx, maxy = city_wgs.total_bounds
pad = 0.02
big_box = box(minx - pad, miny - pad, maxx + pad, maxy + pad)
city_union = unary_union(city_wgs.geometry)
mask_geom = big_box.difference(city_union)

mask_patch = polygon_to_patch(
    mask_geom,
    facecolor='white',
    edgecolor='none',
    zorder=4,
    linewidth=0
)
ax.add_patch(mask_patch)

# ── City boundary drawn on top of mask ───────────────────────────────────────
city_wgs.boundary.plot(
    ax=ax,
    color='#2C3E50',
    linewidth=1.5,
    linestyle='--',
    zorder=5
)

# ── Zoom to city boundary extent ──────────────────────────────────────────────
ax.set_xlim(minx - pad, maxx + pad)
ax.set_ylim(miny - pad, maxy + pad)

# ── Place name labels with offset leader lines ────────────────────────────────
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
    'dx': [
        -40, -45, -50,  30,
         35,  40,  45,
         35,  20, -40,  20,
        -30,  30,  40
    ],
    'dy': [
        -15, -25, -35,  15,
         20,  30, -15,
         20,  25,  20,  30,
        -20, -20,  20
    ]
})

geometry = [Point(xy) for xy in zip(known_places.lon, known_places.lat)]
places_wgs = gpd.GeoDataFrame(known_places, geometry=geometry, crs='EPSG:4326')

for idx, row in places_wgs.iterrows():
    x, y = row.geometry.x, row.geometry.y
    dx, dy = row['dx'], row['dy']
    ax.plot(x, y, 'o', color='#2C3E50', markersize=4, zorder=6)
    ax.annotate(
        row['name'],
        xy=(x, y),
        xytext=(dx, dy),
        textcoords='offset points',
        fontsize=8.5,
        fontweight='bold',
        color='#1A1A2E',
        ha='center',
        va='center',
        arrowprops=dict(
            arrowstyle='-',
            color='#555555',
            linewidth=0.8,
            shrinkA=0,
            shrinkB=3
        ),
        path_effects=[pe.withStroke(linewidth=2.5, foreground='white')],
        zorder=7
    )

# ── Legend ────────────────────────────────────────────────────────────────────
patches = [mpatches.Patch(color=c, label=l) for l, c in color_map.items()]
patches.append(mpatches.Patch(
    facecolor='none', edgecolor='#2C3E50',
    linestyle='--', linewidth=1.5, label='City Boundary'
))
ax.legend(
    handles=patches,
    loc='lower left',
    fontsize=11,
    title='Land Use Category',
    title_fontsize=12,
    framealpha=0.95,
    edgecolor='#CCCCCC',
    fancybox=True
)

# ── Title & north arrow ───────────────────────────────────────────────────────
ax.set_title(
    'Urban Land Use Map — Kozhikode Municipal Corporation\n'
    'Source: OpenStreetMap | Unclassified features excluded',
    fontsize=15, fontweight='bold', pad=20, color='#2C3E50'
)
ax.text(
    0.99, 0.01,
    'N ↑\nProjection: WGS84\nData: © OSM contributors',
    transform=ax.transAxes,
    ha='right', va='bottom', fontsize=9,
    style='italic', color='#555555',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7)
)

ax.set_axis_off()
plt.tight_layout()
plt.savefig('outputs/landuse_map.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
print("Map saved!")