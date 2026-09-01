import sys
import os
import traceback
from PyQt5.QtCore import Qt  # Added for High-DPI scaling constants
from PyQt5.QtWidgets import QApplication
from ui.dashboard import Dashboard

# Enable High-DPI scaling before creating the QApplication instance
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# def get_resource_path(relative_path):
#     """ Get absolute path to resource, works for dev and for PyInstaller """
#     if hasattr(sys, '_MEIPASS'):
#         return os.path.join(sys._MEIPASS, relative_path)
#     return os.path.join(os.path.abspath("."), relative_path)
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)   # ← read-only, re-extracted every launch
    return os.path.join(os.path.abspath("."), relative_path)
def global_exception_handler(exctype, value, tb):
    print("Unhandled Exception:")
    traceback.print_exception(exctype, value, tb)

sys.excepthook = global_exception_handler

if __name__ == "__main__":  
    app = QApplication(sys.argv)

    screen = app.primaryScreen().geometry()
    screen_width = screen.width()
    screen_height = screen.height()

    is_small_screen = screen_width <= 1280 and screen_height <= 800

    window = Dashboard(fullscreen=is_small_screen)

    if is_small_screen:
        window.showFullScreen()
    else:
        window.resize(1200, screen_height - 40)
        window.move(
            (screen_width - 1200) // 2,
            0
        )
        window.show()

    # In PyQt5, use exec_() instead of exec()
    sys.exit(app.exec_())
