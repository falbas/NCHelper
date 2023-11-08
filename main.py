from NCHelper import NCHelper
from datetime import datetime, timedelta
import time
import os

date = datetime.now().replace(hour=12)
nch = None
dir_path = ""
while True:
    date_str = date.strftime("%Y%m%d%H")
    dir_path = f"storage/{date_str}"
    if os.path.exists(dir_path):
        print("already exists")
        break
    
    try:
        nch = NCHelper(
            f"http://182.16.248.173:8080/dods/INA-NWP/{date_str}/{date_str}-d01-asim"
        )
        os.mkdir(dir_path)
        break
    except:
        print(date_str)
        date = date - timedelta(hours=12)
    time.sleep(1)

u = nch.ds["u"]
v = nch.ds["v"]
lat = nch.ds["lat"]
lon = nch.ds["lon"]
nch.nc2asc(u[0][0], lat, lon, f"{dir_path}/U")
nch.nc2asc(v[0][0], lat, lon, f"{dir_path}/V")

tc = nch.ds["tc"]
tc_dir = f"{dir_path}/tc"
os.mkdir(tc_dir)
nch.nc2image(tc[0][0], f"{tc_dir}/tc", x_dim="lon", y_dim="lat", flip=0, cmap="turbo")
nch.geotiff2tiles("C:/Users/falbas/miniconda3/Scripts/gdal2tiles.py", f"{tc_dir}/tc_rgb.tiff", f"{tc_dir}/tiles", "5-7", 16)

psfc = nch.ds["psfc"]
psfc_dir = f"{dir_path}/psfc"
os.mkdir(psfc_dir)
nch.nc2image(psfc[0][0], f"{psfc_dir}/psfc", x_dim="lon", y_dim="lat", flip=0, cmap="turbo")
nch.geotiff2tiles("C:/Users/falbas/miniconda3/Scripts/gdal2tiles.py", f"{psfc_dir}/psfc_rgb.tiff", f"{psfc_dir}/tiles", "5-7", 16)