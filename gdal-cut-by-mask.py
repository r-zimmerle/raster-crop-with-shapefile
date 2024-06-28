import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask

# Paths
shapefile_dir = 'polygons'
input_raster_dir = 'sentinel2-silver'
output_raster_dir = 'sentinel2-gold'

# List of shapefiles
shapefiles = ['polygon-1.shp', 'polygon-2.shp']

# Function to crop and save raster
def crop_and_save_raster(input_raster_path, output_raster_path, geometries, src):
    out_image, out_transform = mask(src, geometries, crop=True)
    out_meta = src.meta
    out_meta.update({
        "driver": "GTiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform
    })
    with rasterio.open(output_raster_path, "w", **out_meta) as dest:
        dest.write(out_image)
    print(f"Raster saved at: {output_raster_path}")

# Process each shapefile
for shapefile_name in shapefiles:
    shapefile_path = os.path.join(shapefile_dir, shapefile_name)
    shapefile = gpd.read_file(shapefile_path)
    print(f"Processing shapefile: {shapefile_path}")
    for raster_file in os.listdir(input_raster_dir):
        if raster_file.endswith('.tif'):
            input_raster_path = os.path.join(input_raster_dir, raster_file)
            output_raster_path = os.path.join(output_raster_dir, f"{os.path.splitext(raster_file)[0]}_{os.path.splitext(shapefile_name)[0]}.tif")
            with rasterio.open(input_raster_path) as src:
                if shapefile.crs != src.crs:
                    shapefile = shapefile.to_crs(src.crs)
                geometries = [geometry for geometry in shapefile.geometry]
                crop_and_save_raster(input_raster_path, output_raster_path, geometries, src)
