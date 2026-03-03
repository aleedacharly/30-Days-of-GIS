import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import contextily as ctx
import pandas as pd
import numpy as np
import geodatasets
from shapely.geometry import Point, box, Polygon
from shapely.ops import unary_union
from matplotlib.patches import PathPatch
from matplotlib.path import Path

# ── Load data ─────────────────────────────────────────────────────────────────
gdf = gpd.read_file('data/processed/landuse_classified.geojson')
gdf_wgs = gdf.to_crs(epsg=4326)

city = gpd.read_file('data/raw/kozhikode_boundary.geojson')
city_wgs = city.to_crs(epsg=4326)

# ── Clip city boundary to land only (removes sea) ────────────────────────────
print("Clipping city boundary to coastline...")
land = gpd.read_file(geodatasets.get_path('naturalearth.land'))
land_wgs = land.to_crs(epsg=4326)
local_box = box(75.5, 11.0, 76.1, 11.6)
land_local = land_wgs.clip(local_box)
land_union = unary_union(land_local.geometry)

# Clip the city polygon to land — sea pixels become empty
city_clipped = city_wgs.copy()
city_clipped['geometry'] = city_wgs.geometry.intersection(land_union)
city_clipped = city_clipped[~city_clipped.geometry.is_empty]
print(f"City clipped to land. Area: {city_clipped.to_crs(epsg=32643).geometry.area.sum()/1e6:.1f} km²")

# Re-clip features to the land-only boundary
gdf_wgs = gpd.clip(gdf_wgs, city_clipped)
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

minx, miny, maxx, maxy = city_clipped.total_bounds
pad = 0.02
ax.set_xlim(minx - pad, maxx + pad)
ax.set_ylim(miny - pad, maxy + pad)

# ── 1. Sea colour background ──────────────────────────────────────────────────
ax.set_facecolor('#C8D8E8')

# ── 2. Basemap ────────────────────────────────────────────────────────────────
ctx.add_basemap(
    ax,
    crs=gdf_wgs.crs.to_string(),
    source=ctx.providers.CartoDB.PositronNoLabels,
    alpha=0.6,
    zorder=1
)

# ── 3. White mask outside city boundary ──────────────────────────────────────
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
city_union = unary_union(city_clipped.geometry)
mask_geom = big_box.difference(city_union)

# Land outside city = light grey
ax.add_patch(polygon_to_patch(
    mask_geom, facecolor='#F5F3EF', edgecolor='none', zorder=2, linewidth=0
))

# ── 4. City boundary ──────────────────────────────────────────────────────────
city_clipped.boundary.plot(ax=ax, color='#2C3E50', linewidth=1.5,
                            linestyle='--', zorder=3)

# ── 5. Land use features ──────────────────────────────────────────────────────
layer_order = ['Water', 'Green/Open', 'Transport', 'Industrial', 'Commercial', 'Residential']
for i, cat in enumerate(layer_order):
    subset = gdf_plot[gdf_plot['landuse_class'] == cat]
    if len(subset) == 0:
        continue
    subset.plot(ax=ax, color=color_map[cat], alpha=0.85,
                linewidth=0.2, edgecolor='white', zorder=4+i)

# ── 6. Place labels ───────────────────────────────────────────────────────────
known_places = pd.DataFrame({
    'name': [
        'Palayam', 'Mananchira', 'Calicut Beach', 'Nadakkavu',
        'Arayidathupalam', 'Mavoor Road', 'Medical College',
        'Chevayur', 'Thondayad', 'West Hill', 'Elathur',
        'Beypore', 'Kunnamangalam'
    ],
    'lon': [
        75.7804, 75.7762, 75.7721, 75.7880,
        75.7950, 75.8020, 75.8033,
        75.8100, 75.8180, 75.7950, 75.8300,
        75.8133, 75.8450
    ],
    'lat': [
        11.2588, 11.2530, 11.2490, 11.2650,
        11.2700, 11.2750, 11.2620,
        11.2830, 11.2950, 11.2700, 11.3100,
        11.1733, 11.2350
    ],
    'dx': [-40, -45, -50,  30,  35,  40,  45,  35,  20, -40,  20, -30,  40],
    'dy': [-15, -25, -35,  15,  20,  30, -15,  20,  25,  20,  30, -20, 20]
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

# ── 7. India inset — hand-drawn polygon (no download needed) ─────────────────
ax_inset = fig.add_axes([0.67, 0.72, 0.22, 0.20])

# India outline as a hand-drawn approximate polygon
india_coords = [
    (68.1, 23.6), (69.0, 22.0), (70.0, 20.5), (70.5, 21.0),
    (72.0, 20.0), (72.6, 21.6), (72.8, 22.0), (73.0, 23.0),
    (74.0, 23.0), (75.0, 23.5), (76.0, 23.5), (77.0, 23.0),
    (78.0, 24.0), (79.0, 24.5), (80.0, 24.0), (81.0, 24.5),
    (82.0, 24.0), (83.0, 24.5), (84.0, 24.0), (85.0, 24.5),
    (86.0, 24.0), (87.0, 24.5), (88.0, 24.0), (88.5, 22.0),
    (89.0, 22.5), (90.0, 22.0), (91.0, 23.5), (92.0, 24.0),
    (92.5, 22.0), (93.0, 22.5), (94.0, 22.0), (95.0, 21.0),
    (97.0, 20.0), (97.5, 18.0), (96.0, 16.0), (95.0, 14.0),
    (94.0, 13.0), (93.0, 13.5), (92.5, 11.0), (92.0, 10.0),
    (91.0, 9.0),  (90.0, 8.5),  (89.0, 8.0),  (88.0, 7.5),
    (80.0, 6.0),  (78.0, 7.5),  (77.5, 8.0),  (77.0, 8.5),
    (76.5, 8.5),  (76.0, 9.0),  (77.0, 10.0), (76.5, 11.0),
    (75.5, 12.0), (74.5, 14.0), (73.5, 15.0), (73.0, 16.5),
    (72.5, 17.0), (72.0, 18.0), (71.0, 19.5), (70.0, 20.0),
    (69.0, 21.0), (68.5, 22.0), (68.1, 23.6),
]

india_poly = Polygon(india_coords)
india_gdf = gpd.GeoDataFrame(geometry=[india_poly], crs='EPSG:4326')

ax_inset.set_facecolor('#C8D8E8')  # sea blue
india_gdf.plot(ax=ax_inset, color='#D4C5A9', edgecolor='#888888',
               linewidth=0.8, zorder=2)

# Kozhikode marker
ax_inset.plot(75.78, 11.25, 'o', color='#C0392B', markersize=7, zorder=5)
ax_inset.plot(75.78, 11.25, 'o', color='white', markersize=3.5, zorder=6)
ax_inset.annotate('Kozhikode', xy=(75.78, 11.25),
                  xytext=(6, 6), textcoords='offset points',
                  fontsize=6, color='#C0392B', fontweight='bold',
                  zorder=7)

ax_inset.set_xlim(67, 98)
ax_inset.set_ylim(5, 38)
ax_inset.set_aspect('equal')
ax_inset.set_xticks([])
ax_inset.set_yticks([])
for spine in ax_inset.spines.values():
    spine.set_edgecolor('#888888')
    spine.set_linewidth(1)
ax_inset.text(0.5, -0.07, 'Location in India',
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