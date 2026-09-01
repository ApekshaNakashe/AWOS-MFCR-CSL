from ui.common import *
import os
import stat
import struct
import datetime
from cryptography.fernet import Fernet
import time
import datetime
import struct
from ui.accessfile import unlock_file,lock_file
# LOG_FORMAT = "20s20s20s12f20s20s20s20s20s4f"
LOG_FORMAT = (
    "20s20s20s"
    "20s20s20s20s20s20s20s20s20s20s20s20s"
    "20s20s20s20s20s20s20s20s20s20s"
    "2i"
)
KEY = b"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx="
cipher = Fernet(KEY)
RECORD_SIZE = struct.calcsize(LOG_FORMAT)

def init_log_file(self):
    try:
        # self.bin_file = open(self.current_log_file,"ab")
        if os.path.exists(self.current_log_file):
            unlock_file(self.current_log_file)

        self.bin_file = open(self.current_log_file, "ab")
   
    except Exception as e:
        print("init log error:",e)


def save_data_to_csv(self, data_list):
    try:
        
        sys_date = str(data_list[0])
        sys_time = str(data_list[1])
        gps_time = str(data_list[2])
        
        record = struct.pack(
            LOG_FORMAT,

            sys_date.encode()[:20].ljust(20, b"\0"),
            sys_time.encode()[:20].ljust(20, b"\0"),
            gps_time.encode()[:20].ljust(20, b"\0"),

            str(data_list[3]).encode()[:20].ljust(20, b"\0"),
            str(data_list[4]).encode()[:20].ljust(20, b"\0"),
            str(data_list[5]).encode()[:20].ljust(20, b"\0"),
            str(data_list[6]).encode()[:20].ljust(20, b"\0"),
            str(data_list[7]).encode()[:20].ljust(20, b"\0"),
            str(data_list[8]).encode()[:20].ljust(20, b"\0"),
            str(data_list[9]).encode()[:20].ljust(20, b"\0"),
            str(data_list[10]).encode()[:20].ljust(20, b"\0"),
            
            str(data_list[11]).encode()[:20].ljust(20, b"\0"),
            str(data_list[12]).encode()[:20].ljust(20, b"\0"),
            str(data_list[13]).encode()[:20].ljust(20, b"\0"),
            str(data_list[14]).encode()[:20].ljust(20, b"\0"),

            str(data_list[15]).encode()[:20].ljust(20, b"\0"),
            str(data_list[16]).encode()[:20].ljust(20, b"\0"),
            str(data_list[17]).encode()[:20].ljust(20, b"\0"),

            str(data_list[18]).encode()[:20].ljust(20, b"\0"),
            str(data_list[19]).encode()[:20].ljust(20, b"\0"),
            str(data_list[20]).encode()[:20].ljust(20, b"\0"),
            str(data_list[21]).encode()[:20].ljust(20, b"\0"),
            str(data_list[22]).encode()[:20].ljust(20, b"\0"),
            str(data_list[23]).encode()[:20].ljust(20, b"\0"),
            str(data_list[24]).encode()[:20].ljust(20, b"\0"),
    
            int(data_list[25]),
            int(data_list[26]),
        )
       
        encrypted = cipher.encrypt(record)

        # Save encrypted length first
        self.bin_file.write(struct.pack("I", len(encrypted)))

        # Save encrypted data
        self.bin_file.write(encrypted)

        self.bin_file.flush()
        # logging.info(f"struct.pack() Success | Record Size = {len(record)} bytes")
        
        # logging.info("Record written successfully")
        # logging.info(f"Current File Size : {os.path.getsize(self.current_log_file)}")

    except Exception as e:
        # logging.error(f"Save Error : {e}")
        # logging.error(traceback.format_exc())
        print("Save Error:", e)

def finalize_log_file(self):
    print("finalize_log_file called")

    try:
        if hasattr(self, "bin_file"):
            self.bin_file.flush()
            self.bin_file.close()

        print("Calling lock_file...")
        lock_file(self.current_log_file)

    except Exception as e:
        print(e)

# def finalize_log_file(self):
#     try:
#         # logging.info("Closing binary file")

#         if hasattr(self, "bin_file"):

#             self.bin_file.flush()
#             self.bin_file.close()

#         os.chmod(
#             self.current_log_file,
#             stat.S_IREAD
#         )
#         # logging.info("Binary file closed successfully")

#     except Exception as e:

#         print(
#             "finalize log error:",
#             e
#         )


#     try:

#         cutoff = (
#             datetime.datetime.now()
#             - datetime.timedelta(days=183)
#         )

#         for filename in os.listdir(
#             self.log_dir
#         ):

#             if not filename.endswith(".awos"):
#                 continue

#             filepath = os.path.join(
#                 self.log_dir,
#                 filename
#             )

#             try:

#                 file_time = datetime.datetime.fromtimestamp(
#                     os.path.getmtime(filepath)
#                 )

#                 if file_time < cutoff:

#                     os.chmod(
#                         filepath,
#                         stat.S_IWRITE
#                     )

#                     os.remove(filepath)

#                     print(
#                         f"Deleted old log: {filename}"
#                     )

#             except Exception as e:

#                 print(
#                     f"Delete error {filename}: {e}"
#                 )

#     except Exception as e:

#         print(
#             "Cleanup Error:",
#             e
#         )
# # import win32security
# # import ntsecuritycon as con

# # def lock_file_deny_write(path):
# #     """Real OS-level deny — Deny ACE must be FIRST in the DACL to
# #     take priority over any existing inherited Allow ACEs."""
# #     everyone_sid, _, _ = win32security.LookupAccountName("", "SYSTEM")

# #     sd = win32security.GetFileSecurity(
# #         path, win32security.DACL_SECURITY_INFORMATION
# #     )
# #     old_dacl = sd.GetSecurityDescriptorDacl()

# #     new_dacl = win32security.ACL()

# #     # 1. Add the Deny ACE FIRST so it's evaluated before any Allow ACE
# #     new_dacl.AddAccessDeniedAce(
# #         win32security.ACL_REVISION,
# #         con.FILE_GENERIC_WRITE | con.DELETE,
# #         everyone_sid
# #     )

# #     # 2. Re-add all existing ACEs (the inherited Allow rules) AFTER the deny
# #     if old_dacl is not None:
# #         for i in range(old_dacl.GetAceCount()):
# #             ace = old_dacl.GetAce(i)
# #             ace_type = ace[0][0]
# #             ace_mask = ace[1]
# #             ace_sid = ace[2]

# #             if ace_type == win32security.ACCESS_ALLOWED_ACE_TYPE:
# #                 new_dacl.AddAccessAllowedAce(
# #                     win32security.ACL_REVISION, ace_mask, ace_sid
# #                 )
# #             elif ace_type == win32security.ACCESS_DENIED_ACE_TYPE:
# #                 new_dacl.AddAccessDeniedAce(
# #                     win32security.ACL_REVISION, ace_mask, ace_sid
# #                 )
# #             # skip other ACE types (audit, etc.) — not relevant here

# #     sd.SetSecurityDescriptorDacl(1, new_dacl, 0)
# #     win32security.SetFileSecurity(
# #         path, win32security.DACL_SECURITY_INFORMATION, sd
# #     )
#csv  CODE
# from ui.common import *
# import os
# import stat
# import struct
# import datetime
# from cryptography.fernet import Fernet
# import time
# import datetime
# import struct
# import csv

# def init_log_file(self):
#     try:
#         file_exists = os.path.exists(self.current_log_file)

#         self.csv_file = open(
#             self.current_log_file,
#             "a",
#             newline="",
#             encoding="utf-8"
#         )

#         self.csv_writer = csv.writer(self.csv_file)

#         if not file_exists:
#             self.csv_writer.writerow([
#                 "SYS Date", "SYS Time", "GPS Time",
#                 "WSP_Dir", "WSP_spd",
#                 "WSS_Dir", "WSS_spd",
#                 "Rel Wind Dir", "Rel Wind Speed",
#                 "True Wind Dir", "True Wind Speed",
#                 "COG", "SOG", "LOG", "GYRO",
#                 "MODE", "sensor_selection", "sensor_selected",
#                 "latitude", "longitude",
#                 "Humidity", "Dew Point",
#                 "Tempture", "Pressure", "Visiblity",
#                 "Avg", "Stray Limit"
#             ])

#     except Exception as e:
#         print("init log error:", e)

# def save_data_to_csv(self, data_list):
#     try:
#         self.csv_writer.writerow(data_list)
#         self.csv_file.flush()

#     except Exception as e:
#         print("Save Error:", e)

# def finalize_log_file(self):
#     try:
#         if hasattr(self, "csv_file"):
#             self.csv_file.flush()
#             self.csv_file.close()

#         os.chmod(
#             self.current_log_file,
#             stat.S_IREAD
#         )

#     except Exception as e:
#         print("finalize log error:", e)
#eXCEL with password but is not generating
# import os
# import win32com.client

# def init_log_file(self):
#     try:
#         self.excel = win32com.client.Dispatch("Excel.Application")
#         self.excel.Visible = False
#         self.excel.DisplayAlerts = False

#         self.workbook = self.excel.Workbooks.Add()
#         self.sheet = self.workbook.Worksheets(1)

#         headers = [
#             "SYS Date","SYS Time","GPS Time","WSP_Dir","WSP_spd",
#             "WSS_Dir","WSS_spd","Rel Wind Dir","Rel Wind Speed",
#             "True Wind Dir","True Wind Speed","COG","SOG","LOG","GYRO",
#             "MODE","sensor_selection","sensor_selected",
#             "latitude","longitude","Humidity","Dew Point",
#             "Temperature","Pressure","Visibility",
#             "Avg","Stray Limit"
#         ]

#         for col, header in enumerate(headers, start=1):
#             self.sheet.Cells(1, col).Value = header

#         self.current_row = 2

#     except Exception as e:
#         print("init_log_file:", e)

# def save_data_to_csv(self, data_list):
#     try:
#         for col, value in enumerate(data_list, start=1):
#             self.sheet.Cells(self.current_row, col).Value = value

#         self.current_row += 1

#         # Save every row (simple version)
#         self.workbook.Save()

#     except Exception as e:
#         print("Save Error:", e)

# def finalize_log_file(self):
#     try:
#         print("Finalize called")
#         print("current_log_file =", self.current_log_file)

#         path = self.current_log_file

#         # Make sure folder exists
#         os.makedirs(os.path.dirname(path), exist_ok=True)

#         print("Saving to:", path)

#         # IMPORTANT: FileFormat=51 is required for .xlsx
#         self.workbook.SaveAs(
#             Filename=path,
#             FileFormat=51,          # xlOpenXMLWorkbook (.xlsx)
#             Password="Marine123"
#         )

#         print("Saved successfully")

#         self.workbook.Close(False)
#         self.excel.Quit()

#         print("Excel closed")

#     except Exception as e:
#         print("Finalize Error:", e)