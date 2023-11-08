from NCHelper import NCHelper
from datetime import datetime, timedelta
import time
import os

date = datetime.now().replace(hour=00)
ds = None
while True:
    date_str = date.strftime("%Y%m%d%H")
    dir_path = f"storage/{date_str}"
    if os.path.exists(dir_path):
        print("already exists")
        break

    try:
        nch = NCHelper(
            f"http://182.16.248.173:8080/dods/INA-NWP/{date_str}/{date_str}-d01-asim",
            dir_path=dir_path,
        )
        break
    except:
        date = date - timedelta(hours=12)
        
    time.sleep(1)
