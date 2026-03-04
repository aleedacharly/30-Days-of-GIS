import rasterio
from rasterio.mask import mask
import geopandas as gpd

# Get Wayanad boundary
import osmnx as ox
wayanad = ox.geocode_to_gdf("Wayanad, Kerala, India")
wayanad_proj = wayanad.to_crs("EPSG:4326")

with rasterio.open("data/raw/ind_ppp_2020.tif") as src:
    out_image, out_transform = mask(src, wayanad_proj.geometry, crop=True)
    out_meta = src.meta.copy()
    out_meta.update({"height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform})

with rasterio.open("data/raw/worldpop_kerala_100m.tif", "w", **out_meta) as dest:
    dest.write(out_image)

print("Clipped WorldPop saved.")