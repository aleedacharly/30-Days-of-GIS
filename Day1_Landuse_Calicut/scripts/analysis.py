import geopandas as gpd
import pandas as pd

# ── Load data ─────────────────────────────────────────────────────────────────
gdf = gpd.read_file('data/processed/landuse_classified.geojson')
summary = pd.read_csv('outputs/landuse_summary.csv')

print("=" * 60)
print("DAY 1 — KOZHIKODE LAND USE ANALYSIS SUMMARY")
print("=" * 60)

# ── Q1: Total features fetched ────────────────────────────────────────────────
total = len(gdf)
classified = gdf[gdf['landuse_class'] != 'Other']
other = gdf[gdf['landuse_class'] == 'Other']

print(f"\n📊 TOTAL FEATURES")
print(f"   Total OSM features fetched     : {total:,}")
print(f"   Classified features            : {len(classified):,}")
print(f"   Unclassified (Other)           : {len(other):,}")
print(f"   % unclassified                 : {len(other)/total*100:.1f}%")

# ── Q2: Dominant land use by area ─────────────────────────────────────────────
print(f"\n🏙️  LAND USE BY AREA")

# Only polygons have meaningful area
gdf_poly = gdf[gdf.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])].copy()
gdf_poly = gdf_poly[gdf_poly['landuse_class'] != 'Other']

if 'area_sqm' not in gdf_poly.columns:
    gdf_poly = gdf_poly.to_crs(epsg=32643)
    gdf_poly['area_sqm'] = gdf_poly.geometry.area

area_by_class = (
    gdf_poly.groupby('landuse_class')['area_sqm']
    .sum()
    .sort_values(ascending=False)
)
area_by_class_ha = area_by_class / 10000
total_classified_area = area_by_class.sum()

for cat, area in area_by_class.items():
    pct = area / total_classified_area * 100
    print(f"   {cat:<15} : {area/10000:>8.1f} ha  ({pct:.1f}%)")

dominant = area_by_class.idxmax()
dominant_pct = area_by_class.max() / total_classified_area * 100
print(f"\n   ► Dominant land use: {dominant} ({dominant_pct:.1f}% of classified area)")

# ── Q3: Feature count by class ────────────────────────────────────────────────
print(f"\n🔢 FEATURE COUNT BY CLASS")
count_by_class = (
    gdf[gdf['landuse_class'] != 'Other']['landuse_class']
    .value_counts()
)
for cat, count in count_by_class.items():
    print(f"   {cat:<15} : {count:,} features")

# ── Q4: Ward-level analysis ───────────────────────────────────────────────────
print(f"\n🗺️  ZONE-LEVEL BREAKDOWN")

if 'zone' in summary.columns:
    zone_col = 'zone'
elif 'ward' in summary.columns:
    zone_col = 'ward'
else:
    zone_col = summary.columns[0]

zones = summary[zone_col].unique()
print(f"   Zones/wards in dataset: {len(zones)}")

# Dominant class per zone
dominant_per_zone = (
    summary.sort_values('area_sqm', ascending=False)
    .groupby(zone_col)
    .first()
    .reset_index()[[zone_col, 'landuse_class', 'area_ha', 'pct_share']]
)
print(f"\n   Dominant land use per zone:")
for _, row in dominant_per_zone.iterrows():
    print(f"   {row[zone_col]:<30} → {row['landuse_class']:<15} ({row['pct_share']:.1f}%)")

# Zone with highest residential
residential = summary[summary['landuse_class'] == 'Residential']
if len(residential) > 0:
    top_residential = residential.sort_values('pct_share', ascending=False).iloc[0]
    print(f"\n   ► Zone with highest Residential share:")
    print(f"     {top_residential[zone_col]} — {top_residential['pct_share']:.1f}% residential")
    print(f"     Area: {top_residential['area_ha']:.1f} ha")
else:
    print("\n   ► No residential zones found in summary")

# Zone with most green space
green = summary[summary['landuse_class'] == 'Green/Open']
if len(green) > 0:
    top_green = green.sort_values('pct_share', ascending=False).iloc[0]
    print(f"\n   ► Zone with highest Green/Open share:")
    print(f"     {top_green[zone_col]} — {top_green['pct_share']:.1f}% green")
    print(f"     Area: {top_green['area_ha']:.1f} ha")
else:
    print("\n   ► No green/open zones found in summary")

# Zone with most water
water = summary[summary['landuse_class'] == 'Water']
if len(water) > 0:
    top_water = water.sort_values('area_ha', ascending=False).iloc[0]
    print(f"\n   ► Zone with most Water area:")
    print(f"     {top_water[zone_col]} — {top_water['area_ha']:.1f} ha")

# ── Q5: Full area summary table ───────────────────────────────────────────────
print(f"\n📋 FULL SUMMARY TABLE (for README)")
print(f"{'Land Use':<15} {'Area (ha)':>10} {'% of Total':>12}")
print("-" * 40)
for cat, area_ha in area_by_class_ha.items():
    pct = area_ha / area_by_class_ha.sum() * 100
    print(f"{cat:<15} {area_ha:>10.1f} {pct:>11.1f}%")
print("-" * 40)
print(f"{'TOTAL':<15} {area_by_class_ha.sum():>10.1f} {'100.0%':>12}")

# ── Save results to file ──────────────────────────────────────────────────────
results = {
    'total_features': total,
    'classified_features': len(classified),
    'unclassified_features': len(other),
    'unclassified_pct': round(len(other)/total*100, 1),
    'dominant_landuse': dominant,
    'dominant_landuse_pct': round(dominant_pct, 1),
}

results_df = pd.DataFrame([results])
results_df.to_csv('outputs/analysis_summary.csv', index=False)
print(f"\n✅ Full results saved to outputs/analysis_summary.csv")
print("=" * 60)