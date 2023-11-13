import os
import shutil
import subprocess
import xarray as xr
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


class NCHelper:
    def __init__(self, dataset=""):
        if dataset == "":
            return None

        print("reading dataset...")
        try:
            self.ds = xr.open_dataset(dataset)
            print("reading dataset done")
        except:
            print("reading dataset failed")
            raise Exception("reading dataset failed")

    def nc2asc(self, var, lat, lon, output_name):
        # prepare the variables
        var = var.values
        lat = lat.values
        lon = lon.values
        if lat[0] < lat[-1]: # vertical
            lat = np.flip(lat, axis=0)
            var = np.flip(var, axis=0)

        ncols = len(lon)
        nrows = len(lat)
        xllcorner = lon[0]
        yllcorner = lat[-1]
        cellsize = abs(lat[0] - lat[1])
        NODATA_value = -9999
        grid = var

        # generate ascii grid file
        print(f"generating {output_name} ascii grid...")
        output_file = f"{output_name}.asc"
        with open(f"{output_file}", "w") as file:
            file.write(f"ncols {ncols}\n")
            file.write(f"nrows {nrows}\n")
            file.write(f"xllcorner {xllcorner}\n")
            file.write(f"yllcorner {yllcorner}\n")
            file.write(f"cellsize {cellsize}\n")
            file.write(f"NODATA_value {NODATA_value}\n")
            for i in grid:
                for j in i:
                    file.write(f"{j} ")
                file.write("\n")
        print(f"output: {os.getcwd()}/{output_file}".replace("\\", "/"))

    def nc2tiff(self, var, output_name, x_dim, y_dim, color_table):
        # generate gray geotiff image
        print(f"generating {output_name} geotiff images...")
        img_dir = f"{output_name}"
        _var = var.rio.set_spatial_dims(x_dim=x_dim, y_dim=y_dim)
        _var.rio.crs
        _var.rio.write_crs("epsg:4326", inplace=True)
        _var.rio.to_raster(f"{img_dir}.tiff")

        # generate rgb geotiff image
        subprocess.run(
            [
                "gdaldem.exe",
                "color-relief",
                f"{img_dir}.tiff",
                color_table,
                f"{img_dir}_rgb.tiff",
            ]
        )

        print(f"output: {os.getcwd()}/{img_dir}.tiff".replace("\\", "/"))
        print(f"output: {os.getcwd()}/{img_dir}_rgb.tiff".replace("\\", "/"))

    def geotiff2tiles(
        self, gdal2tiles_path, input_tiff, output_dir, zoom="5-7", processes=1
    ):
        # generate the tiles with gdal2tiles.py
        # https://gdal.org/programs/gdal2tiles.html
        subprocess.run(
            [
                "python",
                gdal2tiles_path,
                f"{input_tiff}",
                f"{output_dir}",
                f"--zoom={zoom}",
                f"--processes={processes}",
                "--webviewer=leaflet",
            ]
        )
