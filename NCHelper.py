import os
import subprocess
import xarray as xr
import numpy as np
import rasterio

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
        if lat[0] < lat[-1]:  # vertical
            lat = np.flip(lat, axis=0)
            var = np.flip(var, axis=0)
        avlat = abs(lat[0] - lat[-1]) / len(lat)
        avlon = abs(lon[0] - lon[-1]) / len(lon)

        ncols = len(lon)
        nrows = len(lat)
        xllcorner = lon[0]
        yllcorner = lat[-1]
        cellsize = (avlat + avlon) / 2
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

    def nc2tif(self, var, output_name, x_dim, y_dim):
        # generate gray geotiff image
        print(f"generating {output_name} geotiff images...")
        img_dir = f"{output_name}"
        _var = var.rio.set_spatial_dims(x_dim=x_dim, y_dim=y_dim)
        _var.rio.crs
        _var.rio.write_crs("epsg:4326", inplace=True)
        _var.rio.to_raster(f"{img_dir}.tif")

    def nc2tif2(self, var, output_name, lat, lon, nodata=9999):
        # generate gray geotif image
        var = np.flip(var, axis=0)
        transform = rasterio.transform.from_bounds(west=lon[0],south=lat[0],east=lon[-1],north=lat[-1],width=lon.shape[0],height=lat.shape[0])
        with rasterio.open(
            f"{output_name}.tif",
            "w",
            driver="GTiff",
            height=lat.shape[0],
            width=lon.shape[0],
            count=1,
            dtype=var.dtype,
            crs="+proj=latlong",
            transform=transform,
            nodata=nodata
        ) as dst:
            dst.write(var, 1)

    def nc2rgbtif(self, output_name, color_table):
        img_dir = f"{output_name}"
        # generate rgb geotif image
        # https://gdal.org/programs/gdaldem.html
        print(f"generating {output_name} rgb geotif images...")
        subprocess.run(
            [
                "gdaldem.exe",
                "color-relief",
                f"{img_dir}.tif",
                color_table,
                f"{img_dir}_rgb.tif",
            ]
        )
        print(f"output: {os.getcwd()}/{img_dir}_rgb.tif".replace("\\", "/"))

    def geotif2tiles(
        self, gdal2tiles_path, input_tif, output_dir, zoom="5-7", processes=1
    ):
        # generate the tiles with gdal2tiles.py
        # https://gdal.org/programs/gdal2tiles.html
        subprocess.run(
            [
                "python",
                gdal2tiles_path,
                f"{input_tif}",
                f"{output_dir}",
                f"--zoom={zoom}",
                f"--processes={processes}",
                "--webviewer=leaflet",
            ]
        )
