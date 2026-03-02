# Day 01 — Mapping Urban Land Use in Kozhikode

## Problem Statement
Kozhikode's city planners lack a current, digitally accessible land-use baseline.
Without one, development approvals, infrastructure plans, and zoning decisions are
made with outdated paper maps. This project builds a reproducible, open-data
land-use inventory for the Kozhikode Municipal Corporation area.

## Study Area
Kozhikode (Calicut) Municipal Corporation, Kerala, India.
Approx. 118 km\u00b2 urban area with a population of ~600,000.
![Calicut Map](outputs/subset-kozhikode.png)
## Data Sources
| Dataset              | Source                  | Link                        |
|----------------------|-------------------------|-----------------------------|
| Buildings & land use | OpenStreetMap / OSMnx   | https://overpass-turbo.io   |
| City boundary        | OSMnx geocode API       | Auto-fetched               |
| Ward boundaries      | OSM admin level 8       | Via osmnx                  |

## Methods
1. Fetched OSM features (buildings, land use, amenities) using osmnx.features_from_place()
2. Classified features into 6 categories using tag-based rules
3. Reprojected to UTM Zone 43N (EPSG:32643) for accurate area calculation
4. Performed spatial join with ward boundaries
5. Calculated % area per land-use class per ward
6. Rendered choropleth map with CartoDB Positron basemap

## GIS Concepts Applied
- Vector data loading and CRS reprojection
- Attribute-based feature classification
- Spatial join of polygons to administrative boundaries
- Choropleth mapping with continuous colour scale

## Key Results
[Fill in after completing the analysis]
- Total features fetched: XXX polygons
- Dominant land use: [your finding]
- Ward with highest residential \u25ba [ward name] (XX%)
- Ward with most green space \u25ba [ward name] (XX%)

## Critical Reflection
What would a planner or researcher actually do with this output?
[Write 2-3 sentences based on your actual output]

What are the limitations of the data and method?
- OSM coverage in India is uneven; some buildings may lack 'landuse' tags
- Classification rules are simplified; real LULC surveys use field verification
- Ward boundaries from OSM may not match official KMC ward delineations

What is missing from this analysis?
- Floor area ratio (FAR) data for density analysis
- Temporal comparison (land use change over time)
- Population data joined to land-use classes

## Environment
Python 3.10+, geopandas, osmnx, contextily, matplotlib

## How to Reproduce
```bash
pip install geopandas osmnx contextily matplotlib
python scripts/01_fetch_osm.py
python scripts/02_classify_landuse.py
python scripts/03_map.py
```

## Outputs
- `outputs/landuse_map.png` \u2014 Choropleth map (300 dpi)
- `outputs/landuse_summary.csv` \u2014 Area statistics per ward
- `data/processed/landuse_classified.geojson` \u2014 Classified vector data