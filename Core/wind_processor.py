from ui.common import *
from Core.helper import safe_float
import traceback
# def process_wind_data(self, rws1, rws2, rwd1, rwd2, log_speed, sog_speed,heading,cog_speed):

#         sensor_mode = getattr(self, "sensor_selection", "AUTO").upper()

#         # Safe conversion
#         rws1 = safe_float(rws1)
#         rws2 = safe_float(rws2)
#         rwd1 = safe_float(rwd1)
#         rwd2 = safe_float(rwd2)
#         log_speed = safe_float(log_speed)
#         sog_speed = safe_float(sog_speed)

#         # Default
#         selected_rws = None
#         selected_rwd = None

#         # ---------------- AUTO MODE ----------------
#         if sensor_mode == "AUTO":

#             rws1_invalid = math.isinf(rws1)
#             rws2_invalid = math.isinf(rws2)

#             # BOTH INVALID
#             if rws1_invalid and rws2_invalid:
#                 selected_rws = None
#                 selected_rwd = None

#             # SENSOR1 INVALID → USE SENSOR2
#             elif rws1_invalid:
#                 selected_rws = rws2
#                 selected_rwd = rwd2

#             # SENSOR2 INVALID → USE SENSOR1
#             elif rws2_invalid:
#                 selected_rws = rws1
#                 selected_rwd = rwd1

#             # BOTH VALID → SELECT GREATER SPEED
#             else:

#                 if rws1 >= rws2:
#                     selected_rws = rws1
#                     selected_rwd = rwd1
#                 else:
#                     selected_rws = rws2
#                     selected_rwd = rwd2

#         # ---------------- PORT MODE ----------------
#         elif sensor_mode == "PORT":

#             if math.isinf(rws1):
#                 selected_rws = None
#                 selected_rwd = None
#             else:
#                 selected_rws = rws1
#                 selected_rwd = rwd1

#         # ---------------- STBD MODE ----------------
#         elif sensor_mode == "STBD":

#             if math.isinf(rws2):
#                 selected_rws = None
#                 selected_rwd = None
#             else:
#                 selected_rws = rws2
#                 selected_rwd = rwd2

#         # ================= DEBUG =================
#         print(
#             f"Mode={sensor_mode} | "
#             f"RWS1={rws1}, RWD1={rwd1} | "
#             f"RWS2={rws2}, RWD2={rwd2} | "
#             f"Selected={selected_rws}, {selected_rwd}"
#         )

#        # =========================================================
# # RELATIVE WIND INVALID
# # =========================================================
#         if (
#             selected_rws is None
#             or selected_rwd is None
#             or math.isinf(selected_rws)
#             or math.isinf(selected_rwd)
#         ):
#             return None, None, None, None, None, None
#         # ================= AVERAGING =================
#         raw_rws = selected_rws
#         raw_rwd = selected_rwd
#         avg_rwd,avg_rws = self.rws_averager.add_value(raw_rwd,raw_rws)
#         # avg_rwd = self.rwd_averager.add_value(raw_rwd)
#         # ================= STORE HISTORY =================
#         raw_entry = f"{selected_rwd}"
#         avg_val = f"{avg_rwd}"

#         if not hasattr(self, 'rel_wind_history'):
#             self.rel_wind_history = []

#         self.rel_wind_history.append((raw_entry, avg_val))

#         if len(self.rel_wind_history) > 8:
#             self.rel_wind_history.pop(0)
   
# # Auto refresh pressure window
#         if (hasattr(self, "pressure_dir_list") and self.pressure_dir_list.isVisible()):
#             self.update_pressure_lists()
#         # ================= MODE-BASED SPEED =================
#         if self.current_mode == "GPS":
#             vessel_speed = sog_speed
#             vessel_deg= cog_speed
#         else:
#             vessel_speed = log_speed
#             vessel_deg=heading


#         # =========================================================
#         # LOG/SOG INVALID → TRUE WIND BLANK ONLY
#         # =========================================================
#         if (math.isinf(vessel_speed) or math.isinf(vessel_deg)):
#             return (selected_rws,selected_rwd,avg_rws,avg_rwd,None,None)
#         # ================= TRUE WIND =================
#         tws, twa = calculate_true_wind(self,avg_rws,avg_rwd,vessel_speed,vessel_deg)
#         return selected_rws, selected_rwd, avg_rws, avg_rwd, tws, twa
def process_wind_data(self, rws1, rws2, rwd1, rwd2,
                      log_speed, sog_speed,
                      heading, cog_speed):
    try:
        sensor_mode = getattr(self, "sensor_selection").upper()
        sensor_selected = getattr(self, "sensor_selected").upper()

        # Safe conversion
        rws1 = safe_float(rws1)
        rws2 = safe_float(rws2)
        rwd1 = safe_float(rwd1)
        rwd2 = safe_float(rwd2)
        log_speed = safe_float(log_speed)
        sog_speed = safe_float(sog_speed)

        # ---------------- Existing code unchanged ----------------
        selected_rws = None
        selected_rwd = None

        if sensor_mode == "AUTO":

            rws1_invalid = math.isinf(rws1)
            rws2_invalid = math.isinf(rws2)

            if rws1_invalid and rws2_invalid:
                selected_rws = None
                selected_rwd = None
                self.sensor_selected = ""
            elif rws1_invalid:
                selected_rws = rws2
                selected_rwd = rwd2
                self.sensor_selected = "STBD"

            elif rws2_invalid:
                selected_rws = rws1
                selected_rwd = rwd1
                self.sensor_selected = "PORT"

            else:
                if rws1 >= rws2:
                    selected_rws = rws1
                    selected_rwd = rwd1
                    self.sensor_selected = "PORT"
                else:
                    selected_rws = rws2
                    selected_rwd = rwd2
                    self.sensor_selected = "STBD"
        else:
            if sensor_selected == "PORT":

                if math.isinf(rws1):
                    selected_rws = None
                    selected_rwd = None
                else:
                    selected_rws = rws1
                    selected_rwd = rwd1
                # self.sensor_selected = "PORT"

            elif sensor_selected == "STBD":

                if math.isinf(rws2):
                    selected_rws = None
                    selected_rwd = None
                else:
                    selected_rws = rws2
                    selected_rwd = rwd2
                # self.sensor_selected = "STBD"

            print(
                f"Mode={sensor_mode} | "
                f"RWS1={rws1}, RWD1={rwd1} | "
                f"RWS2={rws2}, RWD2={rwd2} | "
                f"Selected={selected_rws}, {selected_rwd}"
            )

        if (
            selected_rws is None
            or selected_rwd is None
            or math.isinf(selected_rws)
            or math.isinf(selected_rwd)
        ):
            return None, None, None, None, None, None

        raw_rws = selected_rws
        raw_rwd = selected_rwd
        print("UI Avg Count      :", self.avg_count)      # or avg_count
        print("WindAverager Count:", self.rws_averager.count)
        avg_rwd, avg_rws = self.rws_averager.add_value(
            raw_rwd,
            raw_rws
        )

        raw_entry = f"{selected_rwd}"
        avg_val = f"{avg_rwd}"

        if not hasattr(self, "rel_wind_history"):
            self.rel_wind_history = []

        self.rel_wind_history.append((raw_entry, avg_val))

        if len(self.rel_wind_history) > 8:
            self.rel_wind_history.pop(0)

        if (
            hasattr(self, "pressure_dir_list")
            and self.pressure_dir_list.isVisible()
        ):
            self.update_pressure_lists()

        if self.current_mode == "GPS":
            vessel_speed = sog_speed
            vessel_deg = cog_speed
        else:
            vessel_speed = log_speed
            vessel_deg = heading

        if (
            math.isinf(vessel_speed)
            or math.isinf(vessel_deg)
        ):
            return (
                selected_rws,
                selected_rwd,
                avg_rws,
                avg_rwd,
                None,
                None
            )

        tws, twa = calculate_true_wind(
            self,
            avg_rws,
            avg_rwd,
            vessel_speed,
            vessel_deg
        )

        return (
            selected_rws,
            selected_rwd,
            avg_rws,
            avg_rwd,
            tws,
            twa
        )

    except Exception as e:
        print(f"Process Wind Data Error: {e}")
        traceback.print_exc()

        # Return safe values so application never crashes
        return None, None, None, None, None, None    

# def calculate_true_wind(self, app_speed, app_dir,sog,cog):
#         sog_safe = 0.0001 if sog == 0 else sog
#         tws_sq = (sog_safe**2 + app_speed**2 - 2 * sog_safe * app_speed * math.cos(math.radians(app_dir)))
#         tws = math.sqrt(tws_sq)
#         # Angle via Law of Cosines, clamped to avoid acos domain errors
#         ratio = (app_speed**2 - tws**2 - sog_safe**2) / (2 * sog_safe * tws)
#         ratio = max(-1.0, min(1.0, ratio))
#         angle = math.degrees(math.acos(ratio))
#         # TWD based on AWD sign (port negative / starboard positive)
#         if app_dir < 0:
#             twd_raw = cog + 360 - angle
#         elif app_dir > 0:
#             twd_raw = cog + angle
#         else:
#             twd_raw = 0.0

#         # Normalise to 0–360°
#         twd = twd_raw - 360 if twd_raw > 360 else twd_raw
#         return tws, twd


def calculate_true_wind(self, app_speed, app_dir, sog, cog):
    try:
        sog_safe = 0.0001 if sog == 0 else sog

        tws_sq = (
            sog_safe**2 +
            app_speed**2 -
            2 * sog_safe * app_speed *
            math.cos(math.radians(app_dir))
        )

        tws = math.sqrt(tws_sq)

        
        ratio = (
            app_speed**2 -
            tws**2 -
            sog_safe**2
        ) / (2 * sog_safe * tws)

        ratio = max(-1.0, min(1.0, ratio))
        angle = math.degrees(math.acos(ratio))

        if app_dir < 0:
            twd_raw = cog + 360 - angle
        elif app_dir > 0:
              twd_raw = cog + angle
        else:
            twd_raw = 0.0

        # Normalise to 0–360°
        twd = twd_raw - 360 if twd_raw > 360 else twd_raw

        return tws, twd

    except Exception as e:
        print(f"True Wind Calculation Error: {e}")
        traceback.print_exc()
        return None, None