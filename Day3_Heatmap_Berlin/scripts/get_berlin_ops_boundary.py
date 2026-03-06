import osmnx as ox
import geopandas as gpd

# The 12 official Berlin Bezirke
bezirke_names = [
    'Mitte', 'Friedrichshain-Kreuzberg', 'Pankow',
    'Charlottenburg-Wilmersdorf', 'Spandau', 'Steglitz-Zehlendorf',
    'Tempelhof-Schöneberg', 'Neukölln', 'Treptow-Köpenick',
    'Marzahn-Hellersdorf', 'Lichtenberg', 'Reinickendorf'
]

berlin_districts = ox.features_from_place(
    'Berlin, Germany',
    tags={'boundary': 'administrative', 'admin_level': '9'}
)

berlin_districts = berlin_districts.reset_index()
berlin_districts = berlin_districts[['name', 'geometry']]

# Filter to only the 12 Bezirke
berlin_districts = berlin_districts[berlin_districts['name'].isin(bezirke_names)]

# Dissolve duplicates
berlin_districts = berlin_districts.dissolve(by='name').reset_index()

print(berlin_districts.shape)
print(berlin_districts['name'].tolist())

# Save
berlin_districts.to_file('data/raw/berlin_districts.geojson', driver='GeoJSON')
print('Saved!')