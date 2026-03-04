import osmnx as ox
import networkx as nx
import geopandas as gpd
import pickle

#Download Wayanadu drive network
print('Downloading Wayanadu road network from OSM!')
G= ox.graph_from_place('Wayanad,Kerala,India',network_type='drive')

#Adding travel time weights to each edge
#Assuming average speeds by road type(km/h)
G=ox.add_edge_speeds(G)
G=ox.add_edge_travel_times(G)

# Save graph for reuse in Script 2
with open('data/processed/wayanad_network.pkl', 'wb') as f:
    pickle.dump(G, f)


print(f'Network saved: {len(G.nodes)} nodes, {len(G.edges)} edges')


# Export road network as GeoDataFrames for visual check
nodes, edges = ox.graph_to_gdfs(G)
edges.to_file('data/processed/wayanad_roads.geojson', driver='GeoJSON')
print('Road network GeoJSON saved.')
