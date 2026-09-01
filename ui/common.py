import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow,QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,QGroupBox,QRadioButton,QFileDialog,QMessageBox,
                             QFrame,QSpacerItem, QLabel,QComboBox,QListWidgetItem, QPushButton,QLineEdit,QDialog, QTableWidget, QTableWidgetItem, QHeaderView,QFormLayout, QSpinBox,QSizePolicy,QListWidget,QButtonGroup)

import os
from Core.Wind_Gauge  import (NeedleGauge,LinearGauge)
from PyQt5.QtGui import QPixmap,QKeySequence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
# from reader import SerialReader
import csv
import math
import threading
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget,QTextEdit,QProgressBar
from PyQt5.QtGui import QFont,QFontMetrics,QFont,QColor

from PyQt5.QtCore import pyqtSignal,Qt,QTimer, QTime,QSize
import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFrame, QLabel, QGridLayout, QPushButton)
from PyQt5.QtGui import QPixmap, QFont, QPainter, QPen, QColor, QPolygon, QFontMetrics
from PyQt5.QtCore import Qt, QPoint,QRectF

import traceback
import os
import csv
from cryptography.fernet import Fernet
from PyQt5.QtWidgets import QTableView, QAbstractItemView
from PyQt5.QtCore import (
    Qt,
    QAbstractTableModel,
    QThread,
    pyqtSignal,
    QModelIndex,
)
KEY = b"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx="
cipher = Fernet(KEY)
import stat
# ── Model — holds pre-built string lists, zero work in data() ────────────────
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex


import os
import csv
import mmap
import stat
import numpy as np
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableView, QPushButton, QLabel,
    QFileDialog, QMessageBox, QAbstractItemView, QHeaderView
)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QThread, pyqtSignal
from PyQt5.QtGui import QKeySequence


# ----------------------------------------------------------------------
# Read-only table model backed by mmap
# ----------------------------------------------------------------------
import mmap
import struct
from cryptography.fernet import Fernet
import os

from PyQt5.QtCore import (
    Qt,
    QModelIndex,
    QAbstractTableModel
)

from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QPolygon,QBrush
from PyQt5.QtCore import Qt, QPoint
import ctypes
import datetime
from datetime import timedelta
import json
import time
from nptdms.writer import TdmsWriter, ChannelObject
import numpy as np
import re