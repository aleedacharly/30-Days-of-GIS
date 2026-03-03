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


## Datasets Used
| Dataset | Source | Format |
|---------|--------|--------|
| Wayanad road network | OpenStreetMap via OSMnx | In-memory GraphML |
| PHC locations | Overpass Turbo / Kerala DHS | GeoJSON |
| Village centroids | Census 2011 / OSM | GeoJSON |
| Population grid | WorldPop 2020 Kerala 100m | GeoTIFF |


## Method
1. Downloaded drive-mode road network for Wayanad using OSMnx
2. Added travel speeds and travel times to each road edge
3. For each PHC, computed ego_graph subgraphs at 15-min and 30-min radius
4. Generated convex hull isochrone polygons from reachable node sets
5. Dissolved all PHC isochrones for each time band
6. Spatially joined village centroids to classify by access zone
7. Used rasterstats to sum WorldPop population within 500m buffer

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
