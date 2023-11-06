import os
import shutil
import subprocess
import xarray as xr
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


date = "20231030"
dir_path = "storage/" + date
if os.path.exists(dir_path):
    shutil.rmtree(dir_path)
os.mkdir(dir_path)

ds = xr.open_dataset(
    "http://182.16.248.173:8080/dods/INA-NWP/2023102800/2023102800-d01-asim"
)

time = ds["time"]
lev = ds["lev"]
lat = ds["lat"]
lon = ds["lon"]
u = ds["u"]
v = ds["v"]

rainc = ds["rainc"]
rainsh = ds["rainsh"]
rainnc = ds["rainnc"]
tc = ds["tc"]
psfc = ds["psfc"]
rh = ds["rh"]


def nc2asc(var, xtime, xlev, lat, lon, asc_name):
    ncols = len(lon.values)
    nrows = len(lat.values)
    xllcorner = lon[0].values
    yllcorner = lat[-1].values
    cellsize = abs(lat[0].values - lat[1].values)
    NODATA_value = -9999
    grid = var[xtime][xlev].values

    with open(f"{dir_path}/{asc_name}.asc", "w") as file:
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


def nc2image(var, xtime, xlev, img_name, x_dim, y_dim, cmap_name="turbo", flip=None):
    img_dir = f"{dir_path}/{img_name}"
    _var = var[xtime][xlev].rio.set_spatial_dims(x_dim=x_dim, y_dim=y_dim)
    _var.rio.crs
    _var.rio.write_crs("epsg:4326", inplace=True)
    _var.rio.to_raster(f"{img_dir}.tiff")

    var_tiff_raster = rasterio.open(f"{img_dir}.tiff")
    data = var_tiff_raster.read(1)
    if flip != None:
        data = np.flip(data, axis=flip)

    cmap = None
    if ".txt" in cmap_name:
        custom_colors = []
        with open(cmap_name, "r") as file:
            lines = file.readlines()
            for line in lines:
                values = line.split()
                r, g, b = int(values[1]), int(values[2]), int(values[3])
                custom_colors.append((r, g, b))

        custom_colors_normalized = [
            (r / 255, g / 255, b / 255) for r, g, b in custom_colors
        ]
        cmap = ListedColormap(custom_colors_normalized)
    else:
        cmap = plt.get_cmap(cmap_name)

    fig, ax = plt.subplots(figsize=(10, 8))
    img = ax.imshow(data, cmap=cmap)
    ax.set_xticks([])
    ax.set_yticks([])

    fig.savefig(
        f"{img_dir}.png",
        dpi=300,
        bbox_inches="tight",
        transparent=True,
        pad_inches=-0.1,
    )

    colorbar_fig, colorbar_ax = plt.subplots(figsize=(10, 0.3))
    colorbar_fig.colorbar(img, cax=colorbar_ax, orientation="horizontal")

    colorbar_fig.savefig(
        f"{img_dir}_colorbar.png", dpi=300, bbox_inches="tight", transparent=True
    )

    dataset = rasterio.open(f"{img_dir}.png")
    bands = [1, 2, 3]
    data = dataset.read(bands)
    bounds = var_tiff_raster.bounds
    transform = rasterio.transform.from_bounds(
        bounds.left,
        bounds.top,
        bounds.right,
        bounds.bottom,
        data.shape[1],
        data.shape[2],
    )

    with rasterio.open(
        f"{img_dir}_rgb.tiff",
        "w",
        driver="GTiff",
        width=data.shape[1],
        height=data.shape[2],
        count=3,
        dtype=data.dtype,
        nodata=0,
        transform=transform,
        crs=var_tiff_raster.crs,
    ) as dst:
        dst.write(data, indexes=bands)

    var_tiff_raster.close()
    dataset.close()


def geotiff2tiles(file, img_name, processes=1):
    subprocess.run(
        [
            "python",
            "C:/Users/falbas/miniconda3/Scripts/gdal2tiles.py",
            "--zoom=5-7",
            f"{file}",
            f"{dir_path}/tiles/{img_name}",
            f"--processes={processes}",
        ]
    )


nc2asc(u, 0, 0, lat, lon, "U")
nc2asc(u, 0, 0, lat, lon, "V")
nc2image(tc, 0, 0, "tc", x_dim="lon", y_dim="lat", flip=0)
geotiff2tiles(
    "D:/Kuliah/MBKM/PKKM BMKG/tes-netcdf/storage/20231029/tc_rgb.tiff", "tc", 4
)
