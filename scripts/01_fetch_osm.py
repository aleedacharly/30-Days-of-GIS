import osmnx as ox
import geopandas as gpd
import warnings
warnings.filterwarnings('ignore')

# Get city boundary polygon
city = ox.geocode_to_gdf('Kozhikode, Kerala, India')
print('CRS:', city.crs)
print('Geometry type:', city.geometry.type.values)

# Save boundary
city.to_file('data/raw/kozhikode_boundary.geojson', driver='GeoJSON')
print('Boundary saved!')

place = 'Kozhikode, Kerala, India'

# Fetch by tag categories
tags_landuse = {'landuse': True}
tags_buildings = {'building': True}
tags_leisure = {'leisure': True}
tags_natural = {'natural': ['water', 'wood', 'grassland']}

landuse = ox.features_from_place(place, tags=tags_landuse)
buildings = ox.features_from_place(place, tags=tags_buildings)
leisure = ox.features_from_place(place, tags=tags_leisure)
natural_feat = ox.features_from_place(place, tags=tags_natural)

print(f'Land use features: {len(landuse)}')
print(f'Building features: {len(buildings)}')
print(f'Leisure features: {len(leisure)}')

# Save raw OSM data
all_features = gpd.pd.concat([landuse, buildings, leisure, natural_feat])
all_features.to_file('data/raw/osm_features.geojson', driver='GeoJSON')
