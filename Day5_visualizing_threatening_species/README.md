# 🦡 Threatened Mammals in Europe — Interactive Species Range Map

An interactive geospatial visualization mapping the range distributions of
threatened mammal species across Europe, built with Python and IUCN Red List
spatial data. Each species polygon is rendered with a unique color, with
full taxonomic metadata accessible via hover tooltips.

## 🗺️ What It Shows

Each polygon represents the **known geographic range** of a threatened mammal
species assessed under the IUCN Red List. The map renders all species
simultaneously, revealing:

- **Spatial overlap** between threatened species ranges
- **Biodiversity hotspots** — regions with high concentrations of overlapping ranges
- **Range size disparities** — from wide-ranging carnivores to narrowly
  endemic species

The dense overlay of overlapping polygons produces an emergent heatmap effect,
where regions with the brightest concentration (Central and Eastern Europe,
the Balkans) indicate the highest richness of threatened mammal ranges.

## 🛰️ Data Source

- **IUCN Red List Spatial Data** — official species range polygons for
  mammals assessed as Vulnerable (VU), Endangered (EN), or
  Critically Endangered (CR)
- Filtered to the European extent using `geopandas` spatial operations

## 🧰 Tech Stack

| Tool | Purpose |
|---|---|
| `geopandas` | Spatial data loading and filtering |
| `folium` | Interactive Leaflet.js map rendering |
| `matplotlib` | HSV colormap generation for per-species coloring |
| `numpy` | Color normalization across species |
| CartoDB Dark Matter | Base tile layer for visual contrast |

## 🚀 How to Run

```bash
git clone https://github.com/YOUR_USERNAME/threatened-mammals-europe.git
cd threatened-mammals-europe
pip install geopandas folium matplotlib numpy
```

Download IUCN mammal range data from:
[https://www.iucnredlist.org/resources/spatial-data-download](https://www.iucnredlist.org/resources/spatial-data-download)

Then run:
```bash
jupyter notebook threatened_mammals.ipynb
```

Open `threatened_species_europe.html` in any browser for the
full interactive experience.

## 🖱️ Interactive Features

- **Hover** over any polygon to reveal species information:
  - Scientific name
  - IUCN species ID
  - Family and Order classification
  - Red List threat category (VU / EN / CR)
- **Zoom and pan** across the full European extent
- Each species is assigned a **unique color** from the HSV spectrum
  for visual differentiation

## 🌱 Why This Matters

Mapping the spatial distribution of threatened species is a foundational
step in conservation planning, protected area prioritization, and
biodiversity monitoring. Visualizing range overlaps at the continental
scale reveals which regions face the highest cumulative pressure from
multiple threatened species simultaneously — information critical for
directing conservation resources effectively.

The Balkans, Central Europe, and parts of the Mediterranean basin
emerge as particularly high-overlap zones, consistent with their
status as recognized European biodiversity hotspots.

## 📌 Key Observations

- **Central and Eastern Europe** display the densest concentration of
  overlapping threatened mammal ranges on the continent
- **The Balkans** emerge as a clear biodiversity hotspot, with numerous
  narrowly endemic species concentrated in a relatively small area
- **The British Isles** show comparatively sparse threatened species
  coverage, reflecting historical island-driven extinction and range
  contraction
- **Iberian Peninsula** contains several endemic threatened species with
  ranges restricted entirely within its boundaries