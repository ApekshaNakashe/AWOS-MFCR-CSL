"""

==================
Read / write the custom comsetup.ini format used by the navigation UI.

File format
-----------
Each entry is two consecutive lines:
    <Key Name><line_number>
    VALUE

Example:
    <Mode Selection><1>
    GPS
    <Sensor Selection><3>
    AUTO

Usage (standalone)
------------------
    from comsetup_config import ComSetupConfig

    cfg = ComSetupConfig("comsetup.ini")
    cfg.load()

    print(cfg.mode)           # "GPS"
    print(cfg.sensor)         # "AUTO"

    cfg.mode = "GYRO-LOG"
    cfg.save()

Usage (as drop-in for the class-method pattern in your existing code)
----------------------------------------------------------------------
    # In your main window class:

    def load_config(self):
        ComSetupConfig.load_into(self, self.config_file)

    def save_config(self):
        ComSetupConfig.save_from(self, self.config_file)
"""

from __future__ import annotations

import os
import re
import traceback
from dataclasses import dataclass, field
from typing import Dict, Optional


# ---------------------------------------------------------------------------
# INI parser / writer
# ---------------------------------------------------------------------------

# Matches lines like  <Mode Selection><1>  or  <NORMAL/NIGHT>
_HEADER_RE = re.compile(r"^<([^>]+)>(?:<\d+>)?$")


def _parse_ini(text: str) -> Dict[str, str]:
    """Return {key: value} from the custom comsetup INI text."""
    result: Dict[str, str] = {}
    lines = [ln.rstrip("\r\n") for ln in text.splitlines()]
    i = 0
    while i < len(lines):
        m = _HEADER_RE.match(lines[i].strip())
        if m:
            key = m.group(1)
            value = lines[i + 1].strip() if i + 1 < len(lines) else ""
            result[key] = value
            i += 2
        else:
            i += 1
    return result


def _build_ini(mapping: Dict[str, str]) -> str:
    """
    Rebuild the INI text from a key→value dict.
    Line numbers are re-generated (odd lines: 1, 3, 5, …).
    """
    lines: list[str] = []
    for idx, (key, value) in enumerate(mapping.items()):
        line_num = idx * 2 + 1
        lines.append(f"<{key}><{line_num}>")
        lines.append(value)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Field definitions – maps INI key → attribute name + default
# ---------------------------------------------------------------------------

@dataclass
class _FieldDef:
    ini_key: str
    attr: str
    default: str


_FIELDS: list[_FieldDef] = [
    _FieldDef("Mode Selection",    "mode",             "GPS"),
    _FieldDef("Sensor Selection",  "sensor_selection", "AUTO"),
    _FieldDef("Sensor Selected",   "sensor_selected",  "PORT"),
    _FieldDef("GPS Offset",        "gps_offset",       "+0:00"),
    _FieldDef("Master Slave",      "master_slave",     "SLAVE"),
    _FieldDef("MFCR Port",         "mfcr_port",        "COM4"),
    _FieldDef("UI Mode",           "ui_mode",          "DAY"),
    _FieldDef("AVG Count",         "avg_count",        "1"),
    _FieldDef("Stray Limit",       "stray_limit",      "40"),
    _FieldDef("NORMAL/NIGHT",      "normal_night",     "NORMAL"),
]

# INI keys that hold integer values
_INT_FIELDS = {"avg_count", "stray_limit"}


# ---------------------------------------------------------------------------
# Main config class
# ---------------------------------------------------------------------------

class ComSetupConfig:
    """
    Represents one comsetup.ini file.

    Attributes mirror the INI keys (see _FIELDS above).
    Integer fields (avg_count, stray_limit) are stored as int.
    All others are str.
    """

    def __init__(self, path: str = "comsetup.ini") -> None:
        self.path = path
        # Set defaults
        for fd in _FIELDS:
            raw = fd.default
            setattr(self, fd.attr, int(raw) if fd.attr in _INT_FIELDS else raw)

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Read self.path and populate attributes."""
        try:
            if not os.path.exists(self.path):
                print(f"[ComSetupConfig] File not found: {self.path!r}  — using defaults.")
                return

            with open(self.path, "r", encoding="utf-8") as fh:
                data = _parse_ini(fh.read())

            for fd in _FIELDS:
                raw = data.get(fd.ini_key, fd.default)
                setattr(self, fd.attr, int(raw) if fd.attr in _INT_FIELDS else raw)

            print(f"[ComSetupConfig] Loaded {self.path!r}")
        except Exception as exc:
            print(f"[ComSetupConfig] Load error: {exc}")
            traceback.print_exc()

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Write current attributes back to self.path."""
        try:
            mapping: Dict[str, str] = {}
            for fd in _FIELDS:
                mapping[fd.ini_key] = str(getattr(self, fd.attr, fd.default))

            with open(self.path, "w", encoding="utf-8") as fh:
                fh.write(_build_ini(mapping))

            print(f"[ComSetupConfig] Saved {self.path!r}")
        except Exception as exc:
            print(f"[ComSetupConfig] Save error: {exc}")
            traceback.print_exc()

    # ------------------------------------------------------------------
    # Drop-in replacements for your existing class-method pattern
    # ------------------------------------------------------------------

    @staticmethod
    def load_into(obj, path: str) -> None:
        """
        Populate *obj* from *path* – mirrors your existing load_config(self).

        Attributes set on obj:
            gps_offset, current_mode (= mode), avg_count (int),
            stray_limit (int), master_slave, sensor_selection,
            mfcr_port, ui_mode, normal_night, sensor_selected.

        If obj has rws_averager / rwd_averager, they are rebuilt after load.
        """
        try:
            cfg = ComSetupConfig(path)
            cfg.load()

            obj.gps_offset       = cfg.gps_offset
            obj.current_mode     = cfg.mode          # keep your existing attr name
            obj.avg_count        = cfg.avg_count      # already int
            obj.stray_limit      = cfg.stray_limit    # already int
            obj.master_slave     = cfg.master_slave
            obj.sensor_selection = cfg.sensor_selection
            obj.mfcr_port        = cfg.mfcr_port
            obj.ui_mode          = cfg.ui_mode
            obj.normal_night     = cfg.normal_night

            # Rebuild averagers if the class uses them
            if hasattr(obj, "rws_averager") or hasattr(obj, "rwd_averager"):
                try:
                    from Core.WindAverager import WindAverager
                    obj.rws_averager = WindAverager(obj.avg_count, obj.stray_limit)
                    obj.rwd_averager = WindAverager(obj.avg_count, obj.stray_limit)
                except ImportError:
                    pass  # WindAverager not available in this context

        except Exception as exc:
            print(f"[ComSetupConfig] load_into error: {exc}")
            traceback.print_exc()

    @staticmethod
    def save_from(obj, path: str) -> None:
        """
        Persist *obj*'s attributes to *path* – mirrors your existing save_config(self).
        """
        try:
            cfg = ComSetupConfig(path)

            cfg.mode             = getattr(obj, "current_mode",     "GPS")
            cfg.gps_offset       = getattr(obj, "gps_offset",       "+0:00")
            cfg.avg_count        = int(getattr(obj, "avg_count",     1))
            cfg.stray_limit      = int(getattr(obj, "stray_limit",   40))
            cfg.master_slave     = getattr(obj, "master_slave",      "SLAVE")
            cfg.sensor_selection = getattr(obj, "sensor_selection",  "AUTO")
            cfg.mfcr_port        = getattr(obj, "mfcr_port",         "COM4")
            cfg.ui_mode          = getattr(obj, "ui_mode",           "DAY")
            cfg.normal_night     = getattr(obj, "normal_night",      "NORMAL")

            cfg.save()

        except Exception as exc:
            print(f"[ComSetupConfig] save_from error: {exc}")
            traceback.print_exc()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        attrs = ", ".join(f"{fd.attr}={getattr(self, fd.attr)!r}" for fd in _FIELDS)
        return f"ComSetupConfig({attrs})"


# ---------------------------------------------------------------------------
# Quick smoke-test  (python comsetup_config.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import tempfile, pathlib

    SAMPLE = """\
<Mode Selection><1>
GPS
<Sensor Selection><3>
AUTO
<Sensor Selected><5>
PORT
<GPS Offset><7>
+0:00
<Master Slave><9>
SLAVE
<MFCR Port><11>
COM4
<UI Mode><13>
DAY
<AVG Count><15>
1
<Stray Limit><17>
40
<NORMAL/NIGHT>
NORMAL
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini",
                                     delete=False, encoding="utf-8") as tmp:
        tmp.write(SAMPLE)
        tmp_path = tmp.name

    # --- Load ---
    cfg = ComSetupConfig(tmp_path)
    cfg.load()
    print("Loaded:", cfg)

    # --- Mutate and save ---
    cfg.mode        = "GYRO-LOG"
    cfg.avg_count   = 4
    cfg.stray_limit = 25
    cfg.gps_offset  = "+5:30"
    cfg.save()

    # --- Reload and verify ---
    cfg2 = ComSetupConfig(tmp_path)
    cfg2.load()
    assert cfg2.mode        == "GYRO-LOG", cfg2.mode
    assert cfg2.avg_count   == 4,          cfg2.avg_count
    assert cfg2.stray_limit == 25,         cfg2.stray_limit
    assert cfg2.gps_offset  == "+5:30",    cfg2.gps_offset
    print("Round-trip OK:", cfg2)

    pathlib.Path(tmp_path).unlink()
    print("\nAll tests passed.")
