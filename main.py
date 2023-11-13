from NCHelper import NCHelper
import os
import shutil

initial_times = ["2023110612", "2023110700", "2023110800"]

for initial_time in initial_times:
    nch = NCHelper(
        f"http://182.16.248.173:8080/dods/INA-NWP/{initial_time}/{initial_time}-d01-asim"
    )

    time = nch.ds["time"]
    times = []
    for t in time.values:
        dt = t.astype("M8[ms]").astype("O")
        times.append(dt.strftime("%Y%m%d%H"))

    level = nch.ds["lev"]
    # levels = [0, 3, 6, 10, 16]
    levels = [0, 3, 6]

    lat = nch.ds["lat"]
    lon = nch.ds["lon"]
    u = nch.ds["u"]
    v = nch.ds["v"]

    vars = ["wspd", "tc", "rh"]

    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = f"storage/{initial_time}"
    os.mkdir(output_dir)
    for i in range(0, len(times)):
        dir_path = f"{output_dir}/{times[i]}"
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.mkdir(dir_path)

        for j in levels:
            dir_path = f"{output_dir}/{times[i]}/{int(level[j].values)}"
            os.mkdir(dir_path)

            wind_dir = f"{dir_path}/wind"
            os.mkdir(wind_dir)
            nch.nc2asc(u[i][j], lat, lon, f"{wind_dir}/U")
            nch.nc2asc(v[i][j], lat, lon, f"{wind_dir}/V")

            # for var in vars:
            #     var_dir = f"{dir_path}/{var}"
            #     os.mkdir(var_dir)
            #     nch.nc2tiff(
            #         nch.ds[var][i][j],
            #         f"{var_dir}/{var}",
            #         x_dim="lon",
            #         y_dim="lat",
            #         color_table=f"{current_dir}/{var}_color.txt",
            #     )
            #     nch.geotiff2tiles(
            #         "C:/Users/falbas/miniconda3/Scripts/gdal2tiles.py",
            #         f"{var_dir}/{var}_rgb.tiff",
            #         f"{var_dir}/tiles",
            #         "5-8",
            #         16,
            #     )
