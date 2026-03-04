# Day 02 — Healthcare Access Gaps via Road Network Analysis in Wayanad


## Problem Statement
Tribal hamlets in Wayanad's hilly terrain are separated from the nearest
Primary Health Centre (PHC) by hours of travel on degraded rural roads.
This project maps which villages fall outside a 30-minute drive-time
threshold to support mobile health unit deployment decisions.


## Region
Wayanad District, Kerala, India


## GIS Concepts Applied
- Road network graph construction with OSMnx
- Drive-time isochrone generation using NetworkX ego_graph
- Spatial join of village centroids to isochrone zones
- Population estimation using WorldPop 100m grid + rasterstats


## Method

### Step 1 — Download PHC Locations (Manual, do this first)
1. Go to https://overpass-turbo.io
2. Paste this query: `[out:json]; area[name="Wayanad"]->.a; (node[amenity=hospital](area.a); node[amenity=clinic](area.a); node[amenity=doctors](area.a);); out body;`
3. Click **Run** → then **Export → Download as GeoJSON**
4. Save as `data/raw/wayanad_phc.geojson`

### Step 2 — Download Village Centroids (Manual, do this second)
1. Go to https://overpass-turbo.io
2. Paste this query: `[out:json]; area[name="Wayanad"]->.a; (node[place=village](area.a); node[place=hamlet](area.a); node[place=town](area.a);); out body;`
3. Click **Run** → then **Export → Download as GeoJSON**
4. Save as `data/raw/wayanad_villages.geojson`

### Step 3 — Download WorldPop Population Grid (Manual, do this third)
1. Download directly from: https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/IND/ind_ppp_2020.tif
2. Save as `data/raw/ind_ppp_2020.tif`

### Step 4 — Build Road Network (Run script 01)
- Automatically downloads Wayanad drive network from OSM
- Adds travel speeds and travel times to each road edge
- Saves network as `data/processed/wayanad_network.pkl`
```bash
python scripts/01_build_network.py
```

### Step 5 — Generate Isochrones (Run script 02)
- Loads the saved road network from Step 4
- For each PHC, computes ego_graph subgraphs at 15-min and 30-min radius
- Generates convex hull isochrone polygons from reachable node sets
- Dissolves all PHC isochrones for each time band
- Saves as `data/processed/isochrone_15min.geojson` and `isochrone_30min.geojson`
```bash
python scripts/02_isochrones.py
```

### Step 6 — Classify Villages & Population (Run script 03)
- Loads villages, isochrones, and WorldPop raster
- Clips WorldPop raster to Wayanad boundary using rasterio mask
- Spatially joins village centroids to classify by access zone (within 15 min / 15-30 min / beyond 30 min)
- Sums WorldPop population within 500m buffer of each village
- Saves `data/processed/villages_classified.geojson` and `outputs/underserved_villages.csv`
```bash
python scripts/03_accessibility_analysis.py
```

### Step 7 — Generate Final Map (Run script 04)
- Loads all processed layers
- Renders isochrone map with colour-coded villages and PHC markers
- Renders bar chart of population by access zone
- Saves final map as `outputs/access_map.png`
```bash
python scripts/04_map.py
```

## Key Results
- Total PHCs mapped: [YOUR VALUE]
- Villages within 15 min: [YOUR VALUE] ([X]%)
- Villages within 30 min: [YOUR VALUE] ([X]%)
- Underserved villages (>30 min): [YOUR VALUE] ([X]%)
- Estimated population beyond 30 min: [YOUR VALUE]
- Top 3 most underserved villages: [NAME1], [NAME2], [NAME3]


## Limitations
- OSM road network in rural Wayanad is incomplete — foot tracks and
  forest paths used by tribal communities are missing.
- Travel speeds are assumed averages; actual road quality in hilly
  terrain may reduce speeds by 30-50%.
- Village centroids from Census 2011 may not reflect current settlement
  locations after 12 years of migration.
- WorldPop model has ±20% error in tribal/forest areas.
- Isochrone method (convex hull) overestimates accessible area in
  areas with rivers or mountain barriers.


## Reflection
What would a planner or researcher do with this output?
[WRITE YOUR ANSWER — think: mobile health units, road upgrade priority,
 budget allocation, policy advocacy]


What is missing from this analysis?
[WRITE YOUR ANSWER — think: foot paths, seasonal road closures,
 actual PHC opening hours, quality of care, not just distance]
