import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt

print("Checking available boundaries...\n")

options = [
    'Kozhikode Municipal Corporation, Kerala, India',
    'Kozhikode city, Kerala, India',
    'Calicut Municipal Corporation, Kerala, India',
    'Kozhikode, Kerala, India',
]

for query in options:
    try:
        gdf = ox.geocode_to_gdf(query)
        area_km2 = gdf.to_crs(epsg=32643).geometry.area.sum() / 1e6
        bounds = gdf.total_bounds
        print(f"Query: {query}")
        print(f"  Area: {area_km2:.1f} km²")
        print(f"  Bounds (minx, miny, maxx, maxy): {bounds.round(4)}")
        print()
    except Exception as e:
        print(f"FAILED: {query} => {e}\n")