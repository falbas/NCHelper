from NCHelper import NCHelper

nch = NCHelper(
    "http://182.16.248.173:8080/dods/INA-NWP/2023102800/2023102800-d01-asim",
    dir_path="storage/tes",
)

u = nch.ds["u"]
v = nch.ds["v"]
lat = nch.ds["lat"]
lon = nch.ds["lon"]
nch.nc2asc(u[0][0], lat, lon, "U")
nch.nc2asc(v[0][0], lat, lon, "V")

tc = nch.ds["tc"]
nch.nc2image(tc[0][0], "tc", x_dim="lon", y_dim="lat", flip=0, cmap="tc_color.txt")