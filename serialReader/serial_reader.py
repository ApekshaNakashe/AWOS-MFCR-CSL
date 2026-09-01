
# import serial
# import json
# from PyQt6.QtCore import QThread, pyqtSignal


# class SerialReader(QThread):

#     data_received = pyqtSignal(dict)
#     raw_sentence_received = pyqtSignal(str)
#     connection_status = pyqtSignal(bool)

#     def __init__(self):
#         super().__init__()

#         self.running = True
#         self.buffer = ""

#         self.load_config()

#     # -----------------------------
#     # Load serial config
#     # -----------------------------
#     def load_config(self):

#         try:
#             with open("config.json", "r") as f:
#                 config = json.load(f)

#             self.port = config["serial"]["port"]
#             self.baudrate = config["serial"]["baudrate"]
#             self.timeout = config["serial"]["timeout"]

#         except Exception as e:

#             print("Config Load Error:", e)
#     # -----------------------------
#     # Serial thread
#     # -----------------------------
#     def run(self):

#         try:

#             # ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
#             self.serial_port = serial.Serial(self.port, self.baudrate, timeout=self.timeout)

#             print("Serial Connected:", self.port)

#             self.connection_status.emit(True)

#             while self.running:

#                 # data = ser.read(ser.in_waiting or 1).decode(errors="ignore")
#                 data = self.serial_port.read(self.serial_port.in_waiting or 1).decode(errors="ignore")

#                 if not data:
#                     continue

#                 self.buffer += data

#                 # Process complete sentences
#                 while "$OTSWD" in self.buffer:

#                     start = self.buffer.index("$OTSWD")

#                     star_index = self.buffer.find("*", start)

#                     # Check checksum exists
#                     if star_index != -1 and len(self.buffer) >= star_index + 3:

#                         end = star_index + 3

#                         sentence = self.buffer[start:end]

#                         # remove processed sentence
#                         self.buffer = self.buffer[end:]

#                         print("Received:", sentence)

#                         # Send raw sentence
#                         self.raw_sentence_received.emit(sentence)

#                         # Parse data
#                         parsed = self.parse_otswd(sentence)

#                         if parsed:
#                             parsed["raw_sentence"] = sentence
#                             self.data_received.emit(parsed)

#                     else:
#                         break

#         except Exception as e:

#             print("Serial Error:", e)

#             self.connection_status.emit(False)

#     # -----------------------------
#     # Stop thread
#     # -----------------------------
#     def stop(self):

#         self.running = False

#         self.quit()

#         self.wait()

#     # -----------------------------
#     # Parse OTSWD sentence
#     # -----------------------------
#     def parse_otswd(self, sentence):

#         try:

#             # Remove checksum part
#             sentence = sentence.split("*")[0]

#             parts = sentence.split(",")

#             if len(parts) < 23:
#                 return None

#             data = {

#                 "gps_time": parts[13],
#                 "latitude": parts[14],
#                 "ns": parts[15],
#                 "longitude": parts[16],
#                 "ew": parts[17],
#                 "date": parts[20],

#                 "humidity": parts[9],
#                 "Temp": parts[10],
#                 "dewP": parts[11],
#                 "Pressure": parts[12],

#                 "visibility": parts[21],
#                 "MIU": parts[22],

#                 "SOG": parts[18],
#                 "CMG": parts[19],

#                 "RelativeWindDirection1": parts[1],
#                 "RelativeWindSpeed1": parts[2],
#                 "RelativeWindSpeed2": parts[5],
#                 "RelativeWindAddress": parts[3],
#                 "RelativeWindDirection2": parts[4],

#                 "log": parts[8],
#                 "heading": parts[7]
#             }

#             return data

#         except Exception as e:

#             print("Parse Error:", e)

#             return None

import sys
import os
import serial
import json
from PyQt5.QtCore import QThread, pyqtSignal

def get_config_path():
    """ Returns the path to config.json right next to the running executable """
    if hasattr(sys, '_MEIPASS'):
        # If running as a compiled EXE, find the directory where the EXE sits
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, "config.json")
    
    # If running normally in development mode, use the local directory
    return os.path.join(os.path.abspath("."), "config.json")


class SerialReader(QThread):
    data_received = pyqtSignal(dict)
    raw_sentence_received = pyqtSignal(str)
    connection_status = pyqtSignal(bool)

    def __init__(self,config_file):
        super().__init__()
        self.running = True
        self.buffer = ""
        self.config_file = config_file
        self.load_config()

    # -----------------------------
    # Load serial config
    # -----------------------------
    # def load_config(self):
    #     try:
    #         config_path = get_config_path()
            
    #         # If the file does not exist, create a clean default template so it doesn't crash
    #         if not os.path.exists(config_path):
    #             default_cfg = {
    #                 "serial": {"port": "COM1", "baudrate": 9600, "timeout": 1},
    #                 "current_mode": "DefaultMode"
    #             }
    #             with open(config_path, "w") as f:
    #                 json.dump(default_cfg, f, indent=4)

    #         with open(config_path, "r") as f:
    #             config = json.load(f)

    #         self.port = config["serial"]["port"]
    #         self.baudrate = config["serial"]["baudrate"]
    #         self.timeout = config["serial"]["timeout"]

    #     except Exception as e:
    #         print("Config Load Error inside Reader Thread:", e)
    def load_config(self):
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
            self.port = config["serial"]["port"]
            self.baudrate = config["serial"]["baudrate"]
            self.timeout = config["serial"]["timeout"]
        except Exception as e:
            print("Config Load Error:", e)
            self.port = "COM1"
            self.baudrate = 9600
            self.timeout = 1
    # -----------------------------
    # Serial thread
    # -----------------------------
    def run(self):
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print("Serial Connected:", self.port)
            self.connection_status.emit(True)

            while self.running:
                data = self.serial_port.read(self.serial_port.in_waiting or 1).decode(errors="ignore")

                if not data:
                    continue

                self.buffer += data

                # Process complete sentences
                while "$OTSWD" in self.buffer:
                    start = self.buffer.index("$OTSWD")
                    star_index = self.buffer.find("*", start)

                    # Check checksum exists
                    if star_index != -1 and len(self.buffer) >= star_index + 3:
                        end = star_index + 3
                        sentence = self.buffer[start:end]

                        # remove processed sentence
                        self.buffer = self.buffer[end:]
                        print("Received:", sentence)

                        # Send raw sentence
                        self.raw_sentence_received.emit(sentence)

                        # Parse data
                        parsed = self.parse_otswd(sentence)
                        if parsed:
                            parsed["raw_sentence"] = sentence
                            self.data_received.emit(parsed)
                    else:
                        break

        except Exception as e:
            print("Serial Error:", e)
            self.connection_status.emit(False)

    # -----------------------------
    # Stop thread
    # -----------------------------
    def stop(self):
        self.running = False
        self.quit()
        self.wait()

    # -----------------------------
    # Parse OTSWD sentence
    # -----------------------------
    def parse_otswd(self, sentence):
        try:
            # Remove checksum part
            sentence = sentence.split("*")[0]
            parts = sentence.split(",")

            if len(parts) < 23:
                return None

            data = {
                "gps_time": parts[13],
                "latitude": parts[14],
                "ns": parts[15],
                "longitude": parts[16],
                "ew": parts[17],
                "date": parts[20],

                "humidity": parts[9],
                "Temp": parts[10],
                "dewP": parts[11],
                "Pressure": parts[12],

                "visibility": parts[21],
                "MIU": parts[22],

                "SOG": parts[18],
                "CMG": parts[19],

                "RelativeWindDirection1": parts[1],
                "RelativeWindSpeed1": parts[2],
                "RelativeWindSpeed2": parts[5],
                "RelativeWindAddress": parts[3],
                "RelativeWindDirection2": parts[4],

                "log": parts[8],
                "heading": parts[7]
            }
            return data
        except Exception as e:
            print("Parse Error:", e)
            return None