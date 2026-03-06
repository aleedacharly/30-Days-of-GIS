import osmnx as ox
berlin = ox.geocode_to_gdf('Berlin, Germany')
berlin.to_file('data/raw/berlin_boundary.geojson', driver='GeoJSON')
print(berlin.crs)