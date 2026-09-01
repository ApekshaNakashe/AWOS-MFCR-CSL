from ui.common import *
import traceback

def safe_int(value):
    try:
        value = str(value).strip().upper()

        if value in ("INF", "+INF", "-INF"):
            return float("INF")

        return int(float(value))

    except Exception as e:
        print(f"safe_int Error: {e}")
        return 0

# def safe_float(value):
#     try:
#         if value is None:
#             return 0.0

#         value = str(value).strip().upper()

#         if value in ("INF", "+INF", "-INF"):
#             return "INF"

#         return float(value)

#     except Exception as e:
#         print(f"safe_float Error: {e}")
#         return 0.0
def safe_float(value):
    try:
        if value is None:
            return 0.0

        value = str(value).strip().upper()

        if value in ("INF", "+INF", "-INF"):
            return float("INF")

        return float(value)

    except Exception as e:
        print(f"safe_float Error: {e}")
        return 0.0

def log_value(value):
    if math.isinf(value):
        return "INF"
    return value
def format_nmea(self, content):
    try:
        checksum = 0

        for char in content:
            checksum ^= ord(char)

        return f"${content}*{checksum:02X}\r\n"

    except Exception as e:
        print(f"format_nmea Error: {e}")
        traceback.print_exc()
        return ""


def safe_display(self, value):
    try:
        if value is None:
            return ""

        value = str(value).strip().upper()

        if value in ["INF", "+INF", "-INF", ""]:
            return ""

        return value

    except Exception as e:
        print(f"safe_display Error: {e}")
        return ""

import math

def safe_display_cog(self, value):
    try:
        if value is None:
            return ""

        # Float/int values
        if isinstance(value, (int, float)):
            if math.isinf(value):
                return ""
            return f"{value:06.2f}"

        # String values
        value = str(value).strip()

        if value.upper() in ("INF", "+INF", "-INF", ""):
            return ""

        # Try formatting numeric strings
        try:
            return f"{float(value):06.2f}"
        except ValueError:
            return value

    except Exception as e:
        print(f"safe_display Error: {e}")
        return ""
def is_invalid(value):
    try:
        return value is None or math.isinf(value)

    except Exception as e:
        print(f"is_invalid Error: {e}")
        return True


def get_offset_time(self, gps_time_str, offset_str):
    try:
        fmt = "%H%M%S.%f"

        t = datetime.datetime.strptime(gps_time_str, fmt)

        sign = 1 if offset_str[0] == '+' else -1

        parts = offset_str[1:].split(':')
        hours = int(parts[0])
        minutes = int(parts[1])

        offset_delta = datetime.timedelta(
            hours=sign * hours,
            minutes=sign * minutes
        )

        new_time = t + offset_delta

        return new_time.strftime("%H:%M:%S")

    except Exception as e:
        print(f"get_offset_time Error: {e}")
        traceback.print_exc()
        return gps_time_str

# def get_offset_time(self, gps_time_str, offset_str):
#     try:
#         if not self.validate_offset(offset_str):
#             return gps_time_str

#         fmt = "%H%M%S.%f"
#         t = datetime.datetime.strptime(gps_time_str, fmt)

#         sign = 1 if offset_str[0] == '+' else -1
#         hours, minutes = map(int, offset_str[1:].split(':'))

#         offset_delta = datetime.timedelta(
#             hours=sign * hours,
#             minutes=sign * minutes
#         )

#         new_time = t + offset_delta

#         return new_time.strftime("%H:%M:%S")

#     except Exception as e:
#         print(f"get_offset_time Error: {e}")
#         return gps_time_str    

import re
from PyQt5.QtWidgets import QMessageBox

def validate_offset(self, offset_str):
    pattern = r'^[+-](\d{1,2}):(\d{2})$'

    match = re.match(pattern, offset_str)

    if not match:
        QMessageBox.warning(
            self,
            "Invalid Offset",
            "Please enter offset in format:\n\n+05:30\n-04:00\n+14:30"
        )
        return False

    hours = int(match.group(1))
    minutes = int(match.group(2))

    if hours > 14 or minutes > 59:
        QMessageBox.warning(
            self,
            "Invalid Offset",
            "Hours must be 0-14 and minutes 0-59."
        )
        return False

    return True