# save as scripts/test_geodatasets.py and run it
import geodatasets
import geopandas as gpd

print("Available datasets:")
print(dir(geodatasets))

# Try loading
try:
    path = geodatasets.get_path('naturalearth.land')
    print(f"\nnaturalearth.land path: {path}")
    gdf = gpd.read_file(path)
    print(f"Columns: {gdf.columns.tolist()}")
    print(f"Rows: {len(gdf)}")
    print(gdf.head(2))
except Exception as e:
    print(f"naturalearth.land failed: {e}")

try:
    path = geodatasets.get_path('naturalearth.countries')
    print(f"\nnaturalearth.countries path: {path}")
    gdf = gpd.read_file(path)
    print(f"Columns: {gdf.columns.tolist()}")
    print(gdf[gdf.columns[0]].head(10))
except Exception as e:
    print(f"naturalearth.countries failed: {e}")