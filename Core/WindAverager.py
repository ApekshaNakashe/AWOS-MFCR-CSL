import traceback
import logging


class WindAverager:
    def __init__(self, count=4, stray_limit=70):
        self.count = count
        self.stray_limit = stray_limit

        
        self.reference = None

        self.dir_values = []
        self.speed_values = []

        self.avg_dir = 0.0
        self.avg_speed = 0.0

        # Speed corresponding to last accepted direction
        self.last_speed = 0.0

        # Logger
        self.logger = logging.getLogger("WindAverager")

        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)

            handler = logging.FileHandler(
                "wind_averager.log",
                encoding="utf-8"
            )

            formatter = logging.Formatter(
                "%(asctime)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(self, msg):
        self.logger.info(msg)
    def add_value(self, direction, speed):

        try:

            if direction in [None, "", "."] or speed in [None, "", "."]:
                return self.avg_dir, self.avg_speed

            direction = float(direction)
            speed = float(speed)

            self.log(f"RECEIVED | DIR={direction:.1f} SPD={speed:.1f}")

            # ----------------------------------------------------
            # First sample
            # ----------------------------------------------------
            if self.reference is None:

                self.reference = direction
                self.last_speed = speed

                self.log(f"FIRST ACCEPTED {direction:.1f}")

                if self.count == 1:
                    self.avg_dir = direction
                    self.avg_speed = speed

                    self.log(
                        f"AVG=1 | DIR={self.avg_dir:.2f} SPD={self.avg_speed:.2f}"
                    )

                    return self.avg_dir, self.avg_speed

                # First sample is always accepted
                self.dir_values.append(direction)
                self.speed_values.append(speed)

                self.log(f"BUFFER={self.dir_values}")

                return self.avg_dir, self.avg_speed

            # ----------------------------------------------------
            # Stray check
            # ----------------------------------------------------
            diff = direction - self.reference

            if diff > 180:
                diff -= 360
            elif diff < -180:
                diff += 360

            accepted = abs(diff) <= self.stray_limit

            # ----------------------------------------------------
            # Accepted
            # ----------------------------------------------------
            if accepted:

                self.reference = direction
                self.last_speed = speed

                if self.count == 1:

                    self.avg_dir = direction
                    self.avg_speed = speed

                    self.log(
                        f"AVG=1 ACCEPTED | DIR={direction:.1f} SPD={speed:.1f}"
                    )

                    return self.avg_dir, self.avg_speed

                self.dir_values.append(direction)
                self.speed_values.append(speed)

                self.log(
                    f"ACCEPTED {direction:.1f} BUFFER={self.dir_values}"
                )

            # ----------------------------------------------------
            # Rejected
            # ----------------------------------------------------
            else:

                self.log(f"REJECTED {direction:.1f}")

                if self.count == 1:

                    self.avg_dir = self.reference
                    self.avg_speed = self.last_speed

                    self.log(
                        f"AVG=1 KEEP LAST | DIR={self.reference:.1f} SPD={self.last_speed:.1f}"
                    )

                    return self.avg_dir, self.avg_speed

                # Duplicate last accepted value
                self.dir_values.append(self.reference)
                self.speed_values.append(self.last_speed)

                self.log(
                    f"DUPLICATED {self.reference:.1f} BUFFER={self.dir_values}"
                )

            # ----------------------------------------------------
            # Calculate Average
            # ----------------------------------------------------
            if len(self.dir_values) == self.count:

                self.avg_dir = sum(self.dir_values) / self.count
                self.avg_speed = sum(self.speed_values) / self.count

                self.log(f"AVERAGE COUNT = {self.count}")
                self.log(f"DIR VALUES = {self.dir_values}")
                self.log(f"SPD VALUES = {self.speed_values}")
                self.log(
                    f"AVG DIR = {self.avg_dir:.2f} | AVG SPD = {self.avg_speed:.2f}"
                )

                # IMPORTANT:
                # Start completely new batch
                self.dir_values.clear()
                self.speed_values.clear()

                self.log("BUFFER RESET = []")

            return self.avg_dir, self.avg_speed

        except Exception as e:

            self.log(f"ERROR | {e}")
            traceback.print_exc()

            return self.avg_dir, self.avg_speed
    #20-7-26
    # def add_value(self, direction, speed):

        try:

            if direction in [None, "", "."] or speed in [None, "", "."]:
                return self.avg_dir, self.avg_speed

            direction = float(direction)
            speed = float(speed)

            self.log(f"RECEIVED | DIR={direction:.1f} SPD={speed:.1f}")

            # ---------------- FIRST SAMPLE ----------------
            if self.reference is None:

                self.reference = direction
                self.last_speed = speed

                self.dir_values = [direction]
                self.speed_values = [speed]

                self.log(f"FIRST ACCEPTED {direction:.1f}")

                # If averaging count is 1
                if self.count == 1:
                    self.avg_dir = direction
                    self.avg_speed = speed

                    self.log(
                        f"AVERAGE COUNT=1 | DIR={self.avg_dir:.2f} SPD={self.avg_speed:.2f}"
                    )

                return self.avg_dir, self.avg_speed

            # ---------------- STRAY CHECK ----------------
            diff = direction - self.reference

            if diff > 180:
                diff -= 360
            elif diff < -180:
                diff += 360

            accepted = abs(diff) <= self.stray_limit

            # =====================================================
            # ACCEPT
            # =====================================================
            if accepted:

                self.reference = direction
                self.last_speed = speed

                # Average = 1
                if self.count == 1:

                    self.avg_dir = direction
                    self.avg_speed = speed

                    self.log(
                        f"AVG=1 ACCEPTED | DIR={direction:.1f} SPD={speed:.1f}"
                    )

                    return self.avg_dir, self.avg_speed

                self.dir_values.append(direction)
                self.speed_values.append(speed)

                self.log(
                    f"ACCEPTED {direction:.1f} "
                    f"BUFFER={self.dir_values}"
                )

            # =====================================================
            # REJECT
            # =====================================================
            else:

                self.log(f"REJECTED {direction:.1f}")

                # Average = 1
                if self.count == 1:

                    self.avg_dir = self.reference
                    self.avg_speed = self.last_speed

                    self.log(
                        f"AVG=1 KEEP LAST | DIR={self.reference:.1f} SPD={self.last_speed:.1f}"
                    )

                    return self.avg_dir, self.avg_speed

                # Duplicate last accepted value
                self.dir_values.append(self.reference)
                self.speed_values.append(self.last_speed)

                self.log(
                    f"DUPLICATED {self.reference:.1f} "
                    f"BUFFER={self.dir_values}"
                )

            # =====================================================
            # CALCULATE AVERAGE
            # =====================================================
            if len(self.dir_values) >= self.count:

                calc_dir = self.dir_values[:self.count]
                calc_spd = self.speed_values[:self.count]

                self.avg_dir = sum(calc_dir) / self.count
                self.avg_speed = sum(calc_spd) / self.count

                self.log(f"AVERAGE COUNT = {self.count}")
                self.log(f"DIR VALUES = {calc_dir}")
                self.log(f"SPD VALUES = {calc_spd}")
                self.log(
                    f"AVG DIR = {self.avg_dir:.2f} | AVG SPD = {self.avg_speed:.2f}"
                )

                # Keep only last accepted value
                self.dir_values = [self.reference]
                self.speed_values = [self.last_speed]

                self.log(f"BUFFER RESET = {self.dir_values}")

            return self.avg_dir, self.avg_speed

        except Exception as e:

            self.log(f"ERROR | {e}")
            traceback.print_exc()

            return self.avg_dir, self.avg_speed