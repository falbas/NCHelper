from NCHelper import NCHelper
import os
import shutil
import time

start_time = time.time()
initial_times = ["2023111412", "2023110800", "2023110700"]
# initial_times = ["2023111412"]

for initial_time in initial_times:
    nch = NCHelper(
        f"http://182.16.248.173:8080/dods/INA-NWP/{initial_time}/{initial_time}-d01-asim"
    )

    tm = nch.ds["time"]
    times = []
    for t in tm.values:
        dt = t.astype("M8[ms]").astype("O")
        times.append(dt.strftime("%Y%m%d%H"))

    level = nch.ds["lev"]
    levels = [0, 3, 6, 10, 16]
    # levels = [0]

    lat = nch.ds["lat"]
    lon = nch.ds["lon"]

    # vars = ["u", "v", "tc", "rh", "wspd", "tp"]
    vars = ["tp"]

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

            for var in vars:
                var_dir = f"{dir_path}/{var}"
                os.mkdir(var_dir)
                if var == "tp":
                    rainc = nch.ds["rainc"][i][j]
                    rainsh = nch.ds["rainsh"][i][j]
                    rainnc = nch.ds["rainnc"][i][j]
                    tp = rainc + rainsh + rainnc
                    nch.nc2tif(tp.values, f"{var_dir}/{var}.tif", lat.values, lon.values)
                else:
                    nch.nc2tif(nch.ds[var][i][j].values, f"{var_dir}/{var}.tif", lat.values, lon.values)

                if var not in ["u", "v"]:
                    nch.gtif2rgbtif(f"{var_dir}/{var}.tif", f"{var_dir}/{var}_rgb.tif", f"{current_dir}/color/{var}_color.txt")
                    nch.tif2img(f"{var_dir}/{var}_rgb.tif", f"{var_dir}/{var}.jpg", format="JPEG")
                    os.remove(f"{var_dir}/{var}.tif")
                    os.remove(f"{var_dir}/{var}_rgb.tif")
                    os.remove(f"{var_dir}/{var}.jpg.aux.xml")
                    # nch.geotif2tiles(
                    #     "C:/Users/falbas/miniconda3/Scripts/gdal2tiles.py",
                    #     f"{var_dir}/{var}_rgb.tif",
                    #     f"{var_dir}",
                    #     "5-8",
                    #     16,
                    # )

                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    print(f"Elapsed Time: {elapsed_time} seconds")