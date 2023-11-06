import os
import shutil
import subprocess
import xarray as xr
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


class NCHelper:
    def __init__(self, dataset, dir_path):
        self.ds = xr.open_dataset(dataset)
        self.dir_path = dir_path

        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.mkdir(dir_path)


nch = NCHelper(
    "sample/indonesia-20230901-20230907.nc",
    "newstorage",
)
