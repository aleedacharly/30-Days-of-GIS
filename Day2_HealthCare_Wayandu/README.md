# Day 02 — Healthcare Access Gaps via Road Network Analysis in Wayanad


## Problem Statement
Tribal hamlets in Wayanad's hilly terrain are separated from the nearest
Primary Health Centre (PHC) by hours of travel on degraded rural roads.
This project maps which villages fall outside a 30-minute drive-time
threshold to support mobile health unit deployment decisions.


## Region
Wayanad District, Kerala, India
![Calicut Map](output/access_map1.png)

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
- Total PHCs mapped: 115
- Villages within 15 min: 225([94.9]%)
- Villages within 30 min: 10 ([4.2]%)
- Underserved villages (>30 min): 2 ([0.8]%)
- Estimated population beyond 30 min: 800
- Top 3 most underserved villages:
   1. Tholpetty (population est: 505)
   2. Thirunelli (population est: 295)


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


## Critical Reflection

### 1. What would a District Medical Officer actually DO with this map?
- **Deploy mobile medical units** to the identified underserved villages (Tholpetty 
  and Thirunelli) on a fixed weekly schedule, prioritising them based on population 
  size and distance from the nearest PHC.
- **Justify road upgrade budget requests** to the Public Works Department by showing 
  which specific road segments, if improved, would bring the most villages within the 
  30-minute threshold — turning a political argument into a spatial evidence-based one.
- **Pre-position emergency obstetric care** — maternal deaths spike in villages beyond 
  30 minutes from a PHC. The DMO could use this map to identify where to station 
  trained birth attendants or set up delivery points closer to underserved hamlets.

### 2. Car travel isochrones vs. tribal car ownership reality
- Wayanad's tribal (Adivasi) population is among the poorest in Kerala. Car ownership 
  in tribal hamlets is estimated below 5%, meaning the vast majority travel by foot, 
  shared auto-rickshaw, or occasional bus. A 30-minute car isochrone likely translates 
  to a 2–3 hour walk for most tribal residents, making the actual underserved population 
  far larger than this analysis shows.
- Redoing this analysis with walking-speed isochrones (network_type='walk', average 
  4 km/h) and auto-rickshaw speeds (~20 km/h on rural roads) would give three separate 
  access maps that together reflect the real spectrum of how people actually travel in 
  Wayanad, rather than a single optimistic car-based estimate.

### 3. How to validate OSM road network accuracy
- **Cross-check against Google Maps or Bhuvan:** Pick 20 random road segments from the 
  OSM network and verify they actually exist by visually checking against Google Maps 
  satellite view or ISRO Bhuvan imagery. If more than 10% are missing or wrong, the 
  network is too incomplete for policy use.
- **Ground-truth with local health workers:** The Wayanad District Medical Office or 
  ASHA workers who travel these routes daily can confirm which roads are passable, which 
  are seasonal, and which are missing entirely from OSM — a phone interview with 5 ASHA 
  workers would be more valuable than any remote validation method.

### 4. Is 30 minutes the right threshold?
- **WHO standard:** The WHO recommends that emergency obstetric care be accessible within 
  2 hours, but for primary care (fever, vaccination, antenatal checkups), 30 minutes is 
  the widely cited operational benchmark used in global health access studies.
- **NITI Aayog standard:** India's Health and Wellness Centre programme under Ayushman 
  Bharat targets a Sub-Health Centre within 3 km and a PHC within 5 km of every 
  household — which in Wayanad's terrain translates to roughly 15–20 minutes by road, 
  meaning even our 30-minute threshold is more lenient than the government's own target.

### 5. How to verify PHC locations and handle errors
- **Cross-reference with official government list:** The Kerala DHS publishes a 
  district-wise PHC directory at dhs.kerala.gov.in. Matching OSM points against this 
  official list by name would quickly identify phantom facilities, duplicates, or 
  mislocated points — if 10% are wrong, remove them and rerun the isochrones, as a 
  single misplaced PHC in a sparse network can shift coverage estimates by 5–10%.
- **Use Google Places API as secondary validation:** Query each PHC name and location 
  against the Google Places API to check if the facility still appears as an active 
  business listing — a closed or relocated PHC will either be missing or flagged as 
  permanently closed, giving a low-cost automated verification step before committing 
  to the analysis.

### 6. Which 3 villages should get the first mobile health unit?
- **1. Tholpetty** — Highest estimated population (505) among underserved villages and 
  located near the Wayanad Wildlife Sanctuary boundary, making permanent infrastructure 
  unlikely due to forest regulations. A mobile unit is the only realistic long-term 
  solution, not a new PHC.
- **2. Thirunelli** — Second highest population (295) and home to a significant Kattunayakan 
  tribal community with historically poor health indicators including high infant mortality 
  and low immunisation rates per NFHS-5 data. High need multiplies the impact of even 
  basic primary care visits.
- **3. The village with the longest travel time to the nearest PHC** — regardless of 
  population size, the village with the greatest network distance represents the highest 
  emergency risk. Even a small hamlet with 50 people where a pregnant woman cannot reach 
  a PHC in time has a measurable maternal mortality risk that justifies prioritisation 
  under equity-based resource allocation frameworks.

## Limitations

- **PHC data quality:** OSM includes private clinics, ayurvedic centres, and 
  individual doctors alongside government PHCs. This inflated the PHC count 
  from a realistic ~38 to 115, causing isochrones to cover almost the entire 
  district and underestimating the true number of underserved villages.

- **Optimistic road travel speeds:** OSMnx assigns standard speed limits to 
  road edges, but Wayanad's mountain roads are narrow, winding, and often 
  degraded. Actual travel times in hilly terrain are likely 1.5–2x longer 
  than the model assumes, meaning the 15-min and 30-min isochrones are 
  significantly larger than reality.

- **Incomplete village layer:** Only 237 villages were returned by the OSM 
  query. Wayanad has over 980 revenue villages. Many tribal hamlets deep in 
  forest areas are entirely unmapped in OSM, meaning the most vulnerable 
  communities are invisible in this analysis.

- **Population underestimation:** With only 800 people estimated beyond 30 
  minutes, the WorldPop model likely undercounts tribal and forest-dwelling 
  populations who live in dispersed, hard-to-survey settlements.

- **Isochrone method overestimates access:** The convex hull approach used to 
  generate isochrone polygons fills in gaps between reachable road nodes, 
  including rivers, hills, and forest areas where no road actually exists. 
  This makes access zones appear larger than they truly are.

- **Static snapshot:** The analysis reflects a single point in time. Seasonal 
  road closures during monsoon (June–September) can cut off tribal hamlets 
  entirely, but this is not captured in the model.

- **PHC opening hours not considered:** A PHC located within 15 minutes is 
  only useful if it is open and staffed. Many rural PHCs in Wayanad operate 
  with skeleton staff or are closed on weekends, which this distance-only 
  model does not account for.