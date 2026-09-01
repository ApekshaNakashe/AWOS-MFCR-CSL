from ui.common import *
from Core.WindAverager import WindAverager
import traceback
def load_config(self):
    try:
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                config = json.load(f)
        else:
            config = {}

        system = config.get("system", {})

        self.gps_offset = system.get("gps_offset", "+5:30")
        self.current_mode = system.get("mode", "GYRO-LOG")
        self.avg_count = int(system.get("avg_count", 4))
        self.stray_limit = int(system.get("stray_limit", 40))
        self.master_slave = system.get("master_slave", "Master")
        self.sensor_selection = system.get("sensor_selection", "AUTO")
        self.sensor_selected = system.get("sensor_selected", "PORT")

        self.rws_averager = WindAverager(
            self.avg_count,
            self.stray_limit
        )

        self.rwd_averager = WindAverager(
            self.avg_count,
            self.stray_limit
        )

    except Exception as e:
        print("Load Config Error:", e)
        traceback.print_exc() 
        
# def save_config(self):
#     try:
#         parent = self.parent()

#         if parent is None:
#             print("Save Config Error: parent is None")
#             return

#         config = {}

#         if os.path.exists(parent.config_file):
#             with open(parent.config_file, "r") as f:
#                 config = json.load(f)

#         config.setdefault("system", {})

#         config["system"]["gps_offset"] = getattr(parent, "gps_offset", "+5:30")
#         config["system"]["mode"] = getattr(parent, "current_mode", "GYRO-LOG")
#         config["system"]["avg_count"] = getattr(parent, "avg_count", 4)
#         config["system"]["stray_limit"] = getattr(parent, "stray_limit", 40)
#         config["system"]["master_slave"] = getattr(parent, "master_slave", "Master")
#         config["system"]["sensor_selection"] = getattr(parent, "sensor_selection", "AUTO")

#         with open(parent.config_file, "w") as f:
#             json.dump(config, f, indent=4)

#     except Exception as e:
#         print("Save Config Error:", e)
#         traceback.print_exc()
def save_config(self):
    try:
        parent = self.parent()

        if parent is None:
            print("Save Config Error: parent is None")
            return

        config = {}

        if os.path.exists(parent.config_file):
            with open(parent.config_file, "r") as f:
                config = json.load(f)

        config.setdefault("system", {})

        config["system"]["gps_offset"] = getattr(parent, "gps_offset", "+5:30")
        config["system"]["mode"] = getattr(parent, "current_mode", "GYRO-LOG")
        config["system"]["avg_count"] = getattr(parent, "avg_count", 4)
        config["system"]["stray_limit"] = getattr(parent, "stray_limit", 40)
        config["system"]["master_slave"] = getattr(parent, "master_slave", "Master")
        config["system"]["sensor_selection"] = getattr(parent, "sensor_selection", "AUTO")

        # ADD THIS
        config["system"]["sensor_selected"] = getattr(parent, "sensor_selected", "PORT")

        with open(parent.config_file, "w") as f:
            json.dump(config, f, indent=4)

    except Exception as e:
        print("Save Config Error:", e)
        traceback.print_exc()