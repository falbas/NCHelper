from NCHelper import NCHelper
from datetime import datetime, timedelta
import time
import os
import sys

# date_str = "2023110800"
# nch = NCHelper(
#     f"http://182.16.248.173:8080/dods/INA-NWP/{date_str}/{date_str}-d01-asim"
# )

date = datetime.now().replace(hour=12)
nch = None
dir_path = ""
limit = 0
while limit <= 100:
    date_str = date.strftime("%Y%m%d%H")
    dir_path = f"storage/{date_str}"
    if os.path.exists(dir_path):
        print("already exists")
        sys.exit(0)

    try:
        nch = NCHelper(
            f"http://182.16.248.173:8080/dods/INA-NWP/{date_str}/{date_str}-d01-asim"
        )
        break
    except:
        date = date - timedelta(hours=12)
        limit += 1
    time.sleep(1)

time = nch.ds["time"]
times = []
for t in time.values:
    dt = t.astype("M8[ms]").astype("O")
    times.append(dt.strftime("%Y%m%d%H"))

lat = nch.ds["lat"]
lon = nch.ds["lon"]
u = nch.ds["u"]
v = nch.ds["v"]
tc = nch.ds["tc"]
psfc = nch.ds["psfc"]

for i in range(0, len(times) - 1, 8):
    dir_path = f"storage/{times[i]}"
    os.mkdir(dir_path)

    wind_dir = f"{dir_path}/wind"
    os.mkdir(wind_dir)
    nch.nc2asc(u[i][0], lat, lon, f"{wind_dir}/U")
    nch.nc2asc(v[i][0], lat, lon, f"{wind_dir}/V")

    tc_dir = f"{dir_path}/tc"
    os.mkdir(tc_dir)
    nch.nc2image(
        tc[0][0], f"{tc_dir}/tc", x_dim="lon", y_dim="lat", flip=0, cmap="turbo"
    )
    nch.geotiff2tiles(
        "C:/Users/falbas/miniconda3/Scripts/gdal2tiles.py",
        f"{tc_dir}/tc_rgb.tiff",
        f"{tc_dir}/tiles",
        "5-7",
        16,
    )

    psfc_dir = f"{dir_path}/psfc"
    os.mkdir(psfc_dir)
    nch.nc2image(
        psfc[0][0], f"{psfc_dir}/psfc", x_dim="lon", y_dim="lat", flip=0, cmap="turbo"
    )
    nch.geotiff2tiles(
        "C:/Users/falbas/miniconda3/Scripts/gdal2tiles.py",
        f"{psfc_dir}/psfc_rgb.tiff",
        f"{psfc_dir}/tiles",
        "5-7",
        16,
    )
