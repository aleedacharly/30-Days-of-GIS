
import geopandas as gpd
import pandas as pd
import rasterstats
import numpy as np


# Load all layers
villages = gpd.read_file('data/raw/wayanad_villages_corrected.geojson').to_crs(epsg=4326)
iso_15 = gpd.read_file('data/processed/isochrone_15min.geojson').to_crs(epsg=4326)
iso_30 = gpd.read_file('data/processed/isochrone_30min.geojson').to_crs(epsg=4326)


# Classify each village
def classify_access(village_gdf, iso_15, iso_30):
    zones = []
    for idx, v in village_gdf.iterrows():
        pt = v.geometry
        if iso_15.contains(pt).any():
            zones.append('Within 15 min')
        elif iso_30.contains(pt).any():
            zones.append('15-30 min')
        else:
            zones.append('Beyond 30 min (Underserved)')
    return zones


villages['access_zone'] = classify_access(villages, iso_15, iso_30)


# Extract WorldPop population estimate per village
# Uses 100m buffer around village centroid
villages_proj = villages.to_crs(epsg=32643)  # UTM Zone 43N for Kerala
villages_proj['buffer'] = villages_proj.geometry.buffer(500)  # 500m buffer
village_buffers = villages_proj.set_geometry('buffer').to_crs(epsg=4326)


stats = rasterstats.zonal_stats(
    village_buffers,
    'data/raw/worldpop_kerala_100m.tif',
    stats=['sum'],
    nodata=-9999
)
villages['population_est'] = [abs(s['sum']) if s['sum'] and s['sum'] > 0 else 0 for s in stats]


# Underserved villages
underserved = villages[villages['access_zone'] == 'Beyond 30 min (Underserved)'].copy()
underserved = underserved.sort_values('population_est', ascending=False)


# Save outputs
villages.to_file('data/processed/villages_classified.geojson', driver='GeoJSON')
underserved[['name', 'access_zone', 'population_est', 'geometry']] \
    .to_csv('outputs/underserved_villages.csv', index=False)


# Summary stats
summary = villages.groupby('access_zone')['population_est'].sum().reset_index()
summary['pct'] = summary['population_est'] / summary['population_est'].sum() * 100
print(summary)
summary.to_csv('outputs/access_zone_summary.csv', index=False)
print(f'Underserved villages: {len(underserved)}')
