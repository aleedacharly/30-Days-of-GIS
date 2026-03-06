# Day 5 — Urban Heat Island Detection and Mapping in Berlin

## Problem Statement
Berlin's 2018 and 2022 summer heat waves caused excess mortality among elderly residents in inner-city districts. The Berlin Senate Department for Urban Development needs a Land Surface Temperature (LST) map at district level to prioritise green-roof subsidies, street-tree planting, and cool-zone infrastructure in the hottest neighbourhoods. This project builds a reproducible, Landsat-based LST mapping workflow and aggregates surface temperatures to Berlin's 12 administrative districts (Bezirke) to provide an evidence base for climate adaptation investment.

---

## Study Area
- **Region:** Berlin, Germany
- **Administrative Units:** 12 Bezirke (districts)
- **Total Area:** ~892 km²
- **Coordinate Reference System:** EPSG:25833 (UTM Zone 33N)
![Berlin heat Map](outputs/ndvi_vs_lst_scatter.png)
---

## Data Sources

| Dataset | Source | Format | Access |
|---------|--------|--------|--------|
| Landsat 8 OLI/TIRS Collection 2 Level-2 | USGS via Google Earth Engine | GeoTIFF | Free |
| Berlin District Boundaries (Bezirke) | OpenStreetMap via OSMnx | GeoJSON | Free/Open |

### Landsat Scene Details
| Property | Value |
|----------|-------|
| Scene ID | LC08_194023_20200601 |
| Acquisition Date | 2020-06-01 |
| Cloud Cover | 0.01% |
| Path / Row | 194 / 023 |
| Collection | Collection 2, Level-2 |
| Processing Note | Mosaic used to ensure full Berlin coverage across Landsat paths 193 and 194 |

---

## Methodology

### Step 1 — Environment Setup
Install required Python packages in a virtual environment:
```bash
python -m venv gis_day5_env
source gis_day5_env/bin/activate
pip install geopandas rasterio rasterstats numpy matplotlib seaborn scipy osmnx
```

Install and authenticate Google Earth Engine:
```bash
pip install earthengine-api
earthengine authenticate
```

### Step 2 — Set Up Folder Structure
Run this from your `gis-30day-challenge/` root directory:
```bash
mkdir -p day05_berlin_urban_heat_island/data/raw
mkdir -p day05_berlin_urban_heat_island/data/processed
mkdir -p day05_berlin_urban_heat_island/scripts
mkdir -p day05_berlin_urban_heat_island/outputs
```

### Step 3 — LST and NDVI Retrieval in Google Earth Engine
Open the GEE Code Editor at https://code.earthengine.google.com and run `scripts/01_lst_gee.js`.

This script:
- Defines Berlin's bounding box: `[13.088, 52.338, 13.761, 52.676]`
- Filters Landsat 8 C2L2 to summer months (June–August), cloud cover < 20%
- Creates a mosaic of all valid scenes to ensure full city coverage (single Landsat path does not cover all of Berlin)
- Converts Band ST_B10 to LST in Celsius: `LST(K) = DN × 0.00341802 + 149.0`, then `LST(°C) = LST(K) − 273.15`
- Computes NDVI from SR_B5 (NIR) and SR_B4 (Red) with scale factor 0.0000275
- Exports `lst_berlin.tif` and `ndvi_berlin.tif` at 30m resolution, EPSG:25833 to Google Drive folder `GEE_Exports`

After running, go to the **Tasks tab** in GEE and click **Run** on both export tasks. Wait for green checkmarks (3–5 minutes).

**Download both files from Google Drive and place them in:**
```
data/raw/lst_berlin.tif
data/raw/ndvi_berlin.tif
```

### Step 4 — Download Berlin District Boundaries
Run `scripts/00_get_districts.py` from inside the `day05_berlin_urban_heat_island/` folder:
```bash
python scripts/00_get_districts.py
```

This fetches the 12 official Bezirke from OpenStreetMap using OSMnx and saves them to:
```
data/raw/berlin_districts.geojson
```

### Step 5 — Zonal Statistics Per District
Run `scripts/02_lst_analysis.py`:
```bash
python scripts/02_lst_analysis.py
```

This script:
- Loads `data/raw/berlin_districts.geojson` and reprojects to EPSG:25833
- Uses rasterio mask to extract LST and NDVI pixel values within each district polygon
- Filters out physically unrealistic pixel values (LST < 15°C or > 55°C) caused by cloud shadow in the mosaic
- Computes mean, min, max, std LST and mean NDVI per district
- Saves results to:
  - `data/processed/berlin_districts_lst.geojson`
  - `outputs/uhi_district_stats.csv`

### Step 6 — Generate Maps and Charts
Run `scripts/03_district_stats.py`:
```bash
python scripts/03_district_stats.py
```
Produces `outputs/lst_map.png` — LST raster with Bezirk boundaries + bar chart ranked hottest to coolest.

Run `scripts/04_map_chart.py`:
```bash
python scripts/04_map_chart.py
```
Produces `outputs/ndvi_vs_lst_scatter.png` — scatter plot of NDVI vs LST per district with regression line.

---

## File Structure

```
day05_berlin_urban_heat_island/
├── data/
│   ├── raw/
│   │   ├── lst_berlin.tif                # LST GeoTIFF from GEE (Celsius, 30m, EPSG:25833)
│   │   ├── ndvi_berlin.tif               # NDVI GeoTIFF from GEE (30m, EPSG:25833)
│   │   └── berlin_districts.geojson      # 12 Bezirke boundaries from OSMnx
│   └── processed/
│       └── berlin_districts_lst.geojson  # Districts enriched with LST and NDVI stats
├── scripts/
│   ├── 00_get_districts.py               # Downloads Berlin district boundaries
│   ├── 01_lst_gee.js                     # GEE script — LST retrieval and export
│   ├── 02_lst_analysis.py                # Zonal statistics per district
│   ├── 03_district_stats.py              # LST map and bar chart
│   └── 04_map_chart.py                   # NDVI vs LST scatter plot
├── outputs/
│   ├── lst_map.png                       # Main heat map with bar chart
│   ├── ndvi_vs_lst_scatter.png           # NDVI vs LST scatter plot
│   └── uhi_district_stats.csv            # Per-district LST and NDVI statistics
└── README.md
```

---

## Key Findings

| Rank | District | Mean LST (°C) | Mean NDVI | Pixel Count |
|------|----------|--------------|-----------|-------------|
| 1 (Hottest) | Marzahn-Hellersdorf | 32.26 | 0.455 | 64,318 |
| 2 | Lichtenberg | 30.49 | 0.367 | 50,277 |
| 3 | Mitte | 29.84 | 0.373 | 38,989 |
| 4 | Pankow | 29.27 | 0.427 | 108,240 |
| 5 | Tempelhof-Schöneberg | 28.17 | 0.345 | 44,654 |
| 6 | Reinickendorf | 27.73 | 0.487 | 88,791 |
| 7 | Charlottenburg-Wilmersdorf | 26.28 | 0.302 | 34,491 |
| 8 | Neukölln | 24.98 | 0.193 | 14,178 |
| 9 | Spandau | 24.96 | 0.402 | 66,550 |
| 10 | Friedrichshain-Kreuzberg | 24.31 | 0.241 | 13,327 |
| 11 | Treptow-Köpenick | 24.20 | 0.403 | 127,807 |
| 12 (Coolest) | Steglitz-Zehlendorf | 23.83 | 0.438 | 72,313 |

- **Hottest district:** Marzahn-Hellersdorf — 32.26°C
- **Coolest district:** Steglitz-Zehlendorf — 23.83°C
- **UHI intensity (hottest vs. coolest):** 8.43°C
- **City mean LST:** ~27.2°C
- **Districts above city mean:** Marzahn-Hellersdorf, Lichtenberg, Mitte, Pankow
- **Max pixel LST recorded:** 48.71°C (Pankow — likely dark rooftop or industrial surface)

---

## Limitations

- **Single mosaic snapshot:** The mosaic combines multiple scenes from the same summer period but LST varies day to day with weather. A multi-date summer mean would be more robust.
- **Cloud shadow filtering:** Pixels below 15°C were removed as physically unrealistic for a Berlin summer day. This threshold is justified but means some valid cool surfaces (large water bodies) may also be excluded.
- **Surface vs. air temperature:** LST measures what the satellite sees — rooftops, roads, tree canopies — not the air temperature people experience at street level. The two are correlated but not identical.
- **30m resolution:** A single pixel may contain a mix of road, building, and garden, reducing the sharpness of hotspot detection within districts.
- **District scale too coarse for planning:** Within a single Bezirk there is enormous variation. Mitte contains both the dense Alexanderplatz area and the Tiergarten park — averaging these loses the detail planners need for block-level decisions.
- **Emissivity correction:** The Level-2 ST product applies a generalised emissivity correction. A surface-specific emissivity dataset (e.g. ASTER EMDE) would improve accuracy over industrial surfaces.

---

## Critical Reflection

**Which district showed the highest LST, and why?**
Marzahn-Hellersdorf recorded the highest mean LST at 32.26°C. This outer district contains extensive Plattenbau (prefabricated concrete) residential blocks built during the GDR era, large commercial and industrial zones, and wide asphalted roads with relatively limited street-tree coverage. The high thermal mass of concrete and dark road surfaces absorbs and re-emits significant heat. Notably, Mitte — the densest urban core — came in third rather than first, partly because it contains the Tiergarten park and the Spree River which act as local cooling features.

Was the NDVI–LST relationship statistically significant?
No — r=0.37, p=0.235, which is not statistically significant at the 0.05 threshold. This means we cannot conclude from this dataset alone that vegetation density drives surface temperature differences at the district scale. Looking at the scatter plot, the cluster of hot inner districts (Marzahn, Lichtenberg, Mitte) all have moderate-to-high NDVI, while cooler outer districts (Steglitz, Treptow, Spandau) also have moderate NDVI — making it impossible to separate the vegetation signal from other factors like land cover type, building density, and proximity to water. This is an important finding in itself: district-level NDVI is too coarse a metric to capture the UHI mechanism. A pixel-level analysis comparing impervious surface fraction directly to LST would likely show a much stronger and clearer relationship.

**How might results differ with a different date?**
A scene from a peak heat wave day (e.g. July 25, 2019 when Berlin reached 38.6°C air temperature) would show much stronger UHI signals and sharper contrast between districts. The ranking of hottest to coolest districts would likely remain similar but the absolute values and UHI intensity would be significantly higher. A post-rain day would suppress LST across the board and reduce inter-district differences. This is why operational UHI monitoring uses multi-year summer means rather than single scenes.

**What would a Berlin Senate planner do with this map?**
A planner would use the district ranking to prioritise intervention zones and cross-reference with population vulnerability data — age structure and income levels. Districts that are both hot AND have high concentrations of elderly or low-income residents would be flagged as double-priority zones for cool infrastructure. The LST raster would identify specific hotspot blocks within districts for street-tree planting and green-roof subsidy targeting. The analysis also provides a baseline — repeat it annually to measure whether interventions are working.

**What are the biggest sources of uncertainty?**
The mosaic approach introduces temporal inconsistency — pixels in different parts of the city may come from different days. The 15°C cloud shadow filter is a manual threshold that could be refined. District-level averaging masks enormous within-district variation. The OSMnx district boundaries may not perfectly match Berlin's official administrative boundaries used in planning documents.

**How would you improve this analysis?**
Use a multi-date summer mean LST from all clear-sky June–August scenes across 3–5 years for a climatological baseline. Disaggregate to LOR Planungsräume (~450 planning units) rather than 12 Bezirke for actionable spatial resolution. Add a social vulnerability layer (elderly population share, income index) to produce a composite heat risk index. Validate LST against ground station air temperature records from Berlin's weather station network. Use ASTER EMDE for surface-specific emissivity correction over industrial areas.

---

## Tools & Environment

- **Google Earth Engine** (JavaScript) — LST and NDVI retrieval and export
- **Python 3.x** — geopandas, rasterio, numpy, matplotlib, scipy, osmnx
- **CRS:** EPSG:25833 (UTM Zone 33N)
- **Landsat Collection:** Collection 2, Level-2 (surface temperature product)

---

## Learning Resources

| Resource | URL |
|----------|-----|
| USGS Landsat C2 L2 Guide | https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products |
| GEE Landsat Tutorial | https://developers.google.com/earth-engine/tutorials/community/landsat-etm-to-oli-harmonization |
| Zhao et al 2014 UHI Review | https://www.nature.com/articles/nclimate2546 |
| Berlin Open Data Portal | https://daten.berlin.de |
| rasterstats docs | https://pythonhosted.org/rasterstats/ |