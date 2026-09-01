import traceback
from ui.common import *
# import
class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.clicked.emit()
        except Exception as e:
            print(f"ClickableLabel Error: {e}")
            traceback.print_exc()
        finally:
            try:
                super().mousePressEvent(event)
            except Exception as e:
                print(f"ClickableLabel Super Error: {e}")

class HoverLabel(QLabel):
    hovered = pyqtSignal()
    left = pyqtSignal()

    def __init__(self, text=""):
        try:
            super().__init__(text)
            self.setMouseTracking(True)
        except Exception as e:
            print(f"HoverLabel Init Error: {e}")
            traceback.print_exc()

    def enterEvent(self, event):
        try:
            self.hovered.emit()
        except Exception as e:
            print(f"HoverLabel Enter Error: {e}")
            traceback.print_exc()
        finally:
            try:
                super().enterEvent(event)
            except Exception as e:
                print(f"HoverLabel Super Enter Error: {e}")

    def leaveEvent(self, event):
        try:
            self.left.emit()
        except Exception as e:
            print(f"HoverLabel Leave Error: {e}")
            traceback.print_exc()
        finally:
            try:
                super().leaveEvent(event)
            except Exception as e:
                print(f"HoverLabel Super Leave Error: {e}")
