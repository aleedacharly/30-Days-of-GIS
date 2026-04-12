# 🌏 Asia Climate Visualization — Temperature × Precipitation Bivariate Map

A bivariate choropleth map of Asia built with Python and TerraClimate 2025 data,
showing the spatial relationship between annual maximum temperature and total
precipitation across the continent.

## 🗺️ What It Shows

Each region is colored by **two variables simultaneously**:
- **X-axis (color warmth):** Annual mean of monthly maximum temperature (°C)
- **Y-axis (color darkness):** Annual total precipitation (mm/year)

The 2D color legend in the bottom-left corner is the key:
| | Cold | Hot |
|---|---|---|
| **Wet** | Blue-green (e.g. Southeast Asia) | Dark teal (e.g. Indonesia) |
| **Dry** | Light beige (e.g. Siberia) | Deep orange (e.g. Arabian Peninsula) |

## 🛰️ Data Source

- **TerraClimate 2025** — high-resolution (~4 km) global monthly climate data
  produced by the Climatology Lab, University of California Merced.
- Variables used: `tmax` (maximum temperature) and `ppt` (precipitation)
- Format: NetCDF4 (`.nc`), processed with `xarray` and `rioxarray`

## 🧰 Tech Stack

| Tool | Purpose |
|---|---|
| `xarray` + `rioxarray` | Load and clip NetCDF climate rasters |
| `geopandas` | Country/continent boundary filtering |
| `matplotlib` | Map rendering and bivariate color mapping |
| `numpy` | Quantile binning for color classification |
| Natural Earth | Country boundary shapefiles |


## 🌱 Why This Matters

Climate patterns directly drive vegetation health, water availability,
agricultural productivity, and biodiversity. Visualizing temperature and
precipitation *together* — rather than separately — reveals climatic zones
that no single variable can show alone. This kind of analysis is foundational
to remote sensing workflows involving NDVI, land cover classification,
and environmental monitoring.

## 📌 Key Observations from the Map

- The **Arabian Peninsula and South Asia** emerge as the hottest and driest zones
- **Indonesia, Malaysia, and the Philippines** show the classic hot-and-wet
  tropical signature — prime zones for dense vegetation and high NDVI
- **Siberia and Central Asia** are cold and dry, consistent with steppe
  and boreal climate regimes
- The **Himalayan foothills and Bangladesh** show a striking wet-and-warm
  signature driven by monsoon systems

  ###### PS: I have got the help from Milan Janosov
