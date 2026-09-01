import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFrame, QLabel, QGridLayout, QPushButton)
from PyQt5.QtGui import QPixmap, QFont, QPainter, QPen, QColor, QPolygon, QFontMetrics
from PyQt5.QtCore import Qt, QPoint

import math
from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QPolygon,QBrush
from PyQt5.QtCore import Qt, QPoint,QRectF

class NeedleGauge(QFrame):
    def __init__(self, mode="white"):
        super().__init__()
        self.setFixedSize(280, 280)
        self.mode = mode
        self.is_night_mode = False
        self.angle = 0
        self.side_indicator = "" 

    def setAngle(self, value):
        self.angle = value % 360
        self.update() # Refresh the screen

    def set_night_mode(self, enabled):
        self.is_night_mode = enabled
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(20, 20, -20, -20)
        center = rect.center()
        radius = rect.width() // 2
        # radius = min(rect.width(), rect.height()) // 2

        if self.mode == "RG":
            p.setPen(QPen(QColor("#000000"), 1))
          
            # p.setBrush(QColor("#64ff00"))
            red_color = QColor("#ff0000")
            if self.is_night_mode:
                 green_color = QColor("#00e3b8")    # Cyan for night mode
        
            else:
                green_color = QColor("#64ff00")    # Normal green
            p.setBrush(red_color)
            p.drawPie(rect, 90 * 16, 180 * 16)
            p.setBrush(green_color)
            p.drawPie(rect, 270 * 16, 180 * 16)
            text_color = Qt.GlobalColor.black
        else:
            p.setBrush(Qt.GlobalColor.white)
            p.drawEllipse(center, radius, radius)
            text_color = Qt.GlobalColor.black

        p.setPen(QPen(text_color, 1))
        p.setFont(QFont("Arial", 9, QFont.Weight.Bold))

        # Draw Ticks and Scale Numbers
        for i in range(0, 361, 10):
            p.save()
            p.translate(center)
            p.rotate(i)
            tick_len = 12 if i % 30 == 0 else 6
            p.drawLine(0, -radius, 0, -radius + tick_len)
            p.restore()

            if i % 30 == 0:
                if self.mode == "RG":
                    # Force 0 at the top, otherwise calculate relative wind (0-180)
                    val = 0 if i == 0 or i == 360 else (i if i <= 180 else 360 - i)
                    self.draw_text(p, center, radius - 25, i, str(val))
                else:
                    # For standard mode, also force 0 at the top
                    val = 0 if i == 0 or i == 360 else i
                    self.draw_text(p, center, radius - 25, i, str(val))


      
        p.save()
        p.translate(center)

        # Determine visual rotation
        if self.mode == "RG":
            display_angle = self.angle if self.angle > 180 else self.angle
        else:
            display_angle = self.angle

        p.rotate(display_angle)

        needle_color = Qt.GlobalColor.black if self.mode == "black" else Qt.GlobalColor.black
        p.setBrush(needle_color)

        points = [QPoint(0, -radius + 10), QPoint(-5, 0), QPoint(5, 0)]
        p.drawPolygon(QPolygon(points))
        p.restore()

        # --- Center Needle Cap ---
        p.setBrush(QColor("black"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(center, 8, 8)

    def draw_text(self, painter, center, r, angle, text):
        painter.save()
        painter.translate(center)
        painter.rotate(angle)
        painter.translate(0, -r)
        fm = QFontMetrics(painter.font())
        tw = fm.horizontalAdvance(text)
        painter.drawText(-tw // 2, 0, text)
        painter.restore()
   


class LinearGauge(QFrame):
    """Vertical SOG Gauge with a wider blue bar and scale numbers"""
    def __init__(self):
        super().__init__()
        # Increased overall widget width from 100 to 120
        self.setFixedWidth(120)
        self.value = 0
        self.night_mode = False
        self.has_value = False

    def set_value(self, val):
    # No data received
        if (
            val is None or
            val == "" or
            (isinstance(val, str) and val.strip().upper() == "INF") or
            (isinstance(val, (int, float)) and math.isinf(val))
        ):
            self.has_value = False
            self.update()
            return

        try:
            self.value = float(val)
            self.value = max(0, min(self.value, 50))
            self.has_value = True
        except (ValueError, TypeError):
            self.has_value = False

        self.update()
    def set_night_mode(self, enabled):
        self.night_mode = enabled
        self.update()
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        if self.night_mode:
           
            text_color = QColor("#e24707")
        else:
           
            text_color = Qt.GlobalColor.white

        # Geometry
        bar_x = 40
        bar_width = 30
        bar_top = 15
        bar_height = 180
        bar_bottom = bar_top + bar_height

        # Background Bar (Grey)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#333"))
        p.drawRoundedRect(
            QRectF(bar_x, bar_top, bar_width, bar_height),
            7, 7
        )

        # Blue Fill
        # Draw blue fill only if a value exists
        if self.has_value:
            fill_h = int((self.value / 50.0) * bar_height)

            # Even 0.0 should show a small blue bar
            fill_h = max(fill_h, 4)

            p.setBrush(QColor("#2196F3"))
            p.drawRoundedRect(
                QRectF(
                    bar_x,
                    bar_bottom - fill_h,
                    bar_width,
                    fill_h
                ),
                7, 7
            )
        # Scale
        p.setPen(QPen(QColor("#9A9797"), 1))
        p.setFont(QFont("Arial", 9))

        for i in range(6):

            scale = 50 - (i * 10)

            y = bar_top + (i * bar_height / 5)

            # Number
            p.drawText(
                QRectF(0, y - 10, 28, 20),
                Qt.AlignRight,
                str(int(scale))
            )

            # Horizontal line
            p.drawLine(
                30,
                int(y),
                bar_x,
                int(y)
            )
     # def paintEvent(self, event):
    #     from PyQt5.QtGui import QPainter, QColor, QFont, QPen
    #     p = QPainter(self)
    #     p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
    #     # Turn off outline pen for shapes to prevent borders
    #     p.setPen(Qt.PenStyle.NoPen)
    #     if self.night_mode:
           
    #         text_color = QColor("#e24707")
    #     else:
           
    #         text_color = Qt.GlobalColor.white
    #     # --- BAR WIDTH SETTINGS ---
    #     # Changed width from 12 to 24.
    #     # Adjusted X position from 35 to 45 to keep it centered properly with the numbers.
    #     bar_x = 45
    #     bar_width = 24
    #     bar_height = 160
    #     bar_top = 10
        
    #     # Scale background (No border)
    #     p.setBrush(QColor("#333"))
    #     p.drawRect(bar_x, bar_top, bar_width, bar_height)
        
    #     # Blue Level (Active SOG - No border)
    #     p.setBrush(QColor("#2255ff"))
    #     fill_h = int((self.value / 50) * bar_height)
    #     bottom = bar_top + bar_height
    #     p.drawRect(bar_x, bottom - fill_h, bar_width, fill_h)
        
    #     # Scale Numbers (Re-enable text pen explicitly)
    #     p.setPen(text_color)
       
    #     p.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        
    #     for i in range(6):
    #         val = 50 - (i * 10)
    #         y = bar_top + (i * 30)
    #         # Adjusted X position of text slightly to make room for the wider bar
    #         p.drawText(10, y + 5, str(val))

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ORIOLE TECHNICAL SOLUTION")
        self.resize(1200, 800)
        self.setStyleSheet("background-color: black; color: white;")
        layout = QHBoxLayout(self)

        # Content Area
        content = QVBoxLayout()
        header = QLabel("ORIOLE TECHNICAL SOLUTION PVT LTD")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        content.addWidget(header)

        # Row for the two different gauges
        g_row = QHBoxLayout()
        self.rel_wind = NeedleGauge(mode="RG")    # 0 to 180
        self.true_wind = NeedleGauge(mode="white") # 0 to 330
        g_row.addWidget(self.rel_wind)
        g_row.addWidget(self.true_wind)
        content.addLayout(g_row)

        sog_container = QHBoxLayout()
        sog_container.addWidget(LinearGauge())
        sog_info = QLabel("133.8 deg\n\n\n\n6.0 kts")
        sog_info.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        sog_container.addWidget(sog_info)
       

        content.addLayout(sog_container)
       
        layout.addLayout(content)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Dashboard()
    w.show()
    sys.exit(app.exec())