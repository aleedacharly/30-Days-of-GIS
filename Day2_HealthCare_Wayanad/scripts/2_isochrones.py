import osmnx as ox
import networkx as nx
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, MultiPolygon
from shapely.ops import unary_union
import pickle, json


# Load the saved network
with open('data/processed/wayanad_network.pkl', 'rb') as f:
    G = pickle.load(f)


# Load PHC locations
phc = gpd.read_file('data/raw/wayanad_phc_corrected.geojson')
phc = phc.to_crs(epsg=4326)  # Ensure WGS84

# Function to compute isochrone polygon for a single point
def get_isochrone(G, lat, lon, travel_time_secs, crs='EPSG:4326'):
    center_node = ox.nearest_nodes(G, lon, lat)
    subgraph = nx.ego_graph(G, center_node, radius=travel_time_secs,
                           distance='travel_time')
    node_points = [Point(G.nodes[n]['x'], G.nodes[n]['y'])
                   for n in subgraph.nodes()]
    if len(node_points) < 3:
        return None
    from shapely.geometry import MultiPoint
    polygon = MultiPoint(node_points).convex_hull.buffer(0.005)
    return polygon


isochrones_15 = []
isochrones_30 = []


for idx, row in phc.iterrows():
    lat = row.geometry.y
    lon = row.geometry.x
    name = row.get('name', f'PHC_{idx}')
    iso_15 = get_isochrone(G, lat, lon, 15 * 60)  # 15 min in secs
    iso_30 = get_isochrone(G, lat, lon, 30 * 60)  # 30 min in secs
    if iso_15:
        isochrones_15.append({'phc_name': name, 'geometry': iso_15, 'time_min': 15})
    if iso_30:
        isochrones_30.append({'phc_name': name, 'geometry': iso_30, 'time_min': 30})
    print(f'Processed: {name}')


# Merge all isochrones and dissolve overlaps
gdf_15 = gpd.GeoDataFrame(isochrones_15, crs='EPSG:4326')
gdf_30 = gpd.GeoDataFrame(isochrones_30, crs='EPSG:4326')


dissolved_15 = gdf_15.dissolve()
dissolved_30 = gdf_30.dissolve()


# Save
dissolved_15.to_file('data/processed/isochrone_15min.geojson', driver='GeoJSON')
dissolved_30.to_file('data/processed/isochrone_30min.geojson', driver='GeoJSON')
print('Isochrones saved.')
