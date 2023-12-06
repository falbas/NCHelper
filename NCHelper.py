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

    def nc2asc(self, var, lat, lon, output):
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
        print(f"generating: {os.getcwd()}/{output}".replace("\\", "/"))
        with open(output, "w") as file:
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
        print(f"output: {os.getcwd()}/{output}".replace("\\", "/"))

    def nc2tif(self, var, output, lat, lon, nodata=-9999):
        # generate gray geotif image
        var = np.flip(var, axis=0)
        transform = rasterio.transform.from_bounds(
            west=lon[0],
            south=lat[0],
            east=lon[-1],
            north=lat[-1],
            width=lon.shape[0],
            height=lat.shape[0],
        )
        print(f"generating: {os.getcwd()}/{output}".replace("\\", "/"))
        with rasterio.open(
            output,
            "w",
            driver="GTiff",
            height=lat.shape[0],
            width=lon.shape[0],
            count=1,
            dtype=var.dtype,
            crs="+proj=latlong",
            transform=transform,
            nodata=nodata,
        ) as dst:
            dst.write(var, 1)
        print(f"output: {os.getcwd()}/{output}".replace("\\", "/"))

    def tif2rgbtif(self, input, output, color_table):
        # https://gdal.org/programs/gdaldem.html
        print(f"generating: {os.getcwd()}/{output}".replace("\\", "/"))
        subprocess.run(["gdaldem", "color-relief", input, color_table, output])
        print(f"output: {os.getcwd()}/{output}".replace("\\", "/"))

    def tif2jpg(self, input, output, color_table="", format="JPEG"):
        # https://gdal.org/programs/gdaldem.html
        print(f"generating: {os.getcwd()}/{output}".replace("\\", "/"))
        subprocess.run(
            [
                "gdaldem",
                "color-relief",
                "-of",
                f"{format}",
                input,
                color_table,
                output,
            ]
        )
        print(f"output: {os.getcwd()}/{output}".replace("\\", "/"))

    def geotif2tiles(self, gdal2tiles_path, input, output_dir, zoom="5-7", processes=1):
        # https://gdal.org/programs/gdal2tiles.html
        print(f"generating: {os.getcwd()}/{output_dir}".replace("\\", "/"))
        subprocess.run(
            [
                "python",
                gdal2tiles_path,
                input,
                output_dir,
                f"--zoom={zoom}",
                f"--processes={processes}",
                "--webviewer=none",
            ]
        )
        print(f"output: {os.getcwd()}/{output_dir}".replace("\\", "/"))
