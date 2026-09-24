# from ui.common import *
# from image import *
# from Core.config_manager import save_config
# from Core.WindAverager import WindAverager
# class ConfigurationWindow(QDialog):
#         def __init__(self, parent=None, mode_label=None):
#             super().__init__(parent)
#             self.mode_lbl = mode_label

#             self.setWindowTitle("WSDS Configuration")
#             self.setFixedSize(500, 500)
#             self.setStyleSheet("background-color: #b3b3b3; color: black; font-family: Arial;")

#             # Base layout for the entire Dialog window
#             main_layout = QVBoxLayout(self)
#             main_layout.setContentsMargins(15, 15, 15, 15)
#             title = QLabel("WIND SPEED AND DIRECTION SYSTEM\nCONFIGURATION\nSensor & Mode selection")
#             title.setAlignment(Qt.AlignmentFlag.AlignCenter)
#             title.setStyleSheet("font-size: 18px; font-weight: bold;color:white;")
#             main_layout.addWidget(title)

#             # Main Tab Widget
#             tabs = QTabWidget()
#             tabs.setStyleSheet("""
#                 QTabWidget::pane { border: 1px solid #7c7c7c; background: #b3b3b3; }
#                 QTabBar::tab { background: #cfcfcf; color: black; padding: 8px 20px; margin-right: 2px; width:100px; }
#                 QTabBar::tab:selected { background: #b3b3b3; font-weight: bold; }
#             """)
#             main_layout.addWidget(tabs)

#             # ------------------ TAB 1: Mode Selection ------------------
#             mode_tab = QWidget()
#             mode_layout = QVBoxLayout(mode_tab)
            
#             mode_layout.setContentsMargins(20, 20, 20, 20)
#             mode_layout.setSpacing(15)

#             # Tab Title
#             self.title_label = QLabel("Mode Selection")
         
#             # self.title_label.setFixedWidth(100)
#             self.title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
#             mode_layout.addWidget(self.title_label)

#             # Single Dynamic Radio Button
#             self.dynamic_radio = QRadioButton()
            
#             radio_style = """
#                 QRadioButton { color: black; font-size: 14px; }
#                 QRadioButton::indicator { width: 18px; height: 18px; }
#                 QRadioButton::indicator:unchecked { border: 2px solid #ababab; background-color: #f2f2f1; border-radius: 10px; }
#                 QRadioButton::indicator:checked { border: 2px solid #ababab; background-color: #f2f2f1; border-radius: 10px; }
#             """
#             self.dynamic_radio.setStyleSheet(radio_style)
#             mode_layout.addWidget(self.dynamic_radio)

#             # Dynamic Status Labels
#             self.textbox = QLabel()
#             self.textbox2 = QLabel()
#             self.textbox.setStyleSheet("font-size: 13px;")
#             self.textbox2.setStyleSheet("font-size: 13px;")
#             mode_layout.addWidget(self.textbox)
#             mode_layout.addWidget(self.textbox2)

#             # Container for GPS Offset elements (Hidden/Shown dynamically)
#             self.gps_offset_container = QWidget()
#             gps_offset_layout = QVBoxLayout(self.gps_offset_container)
#             gps_offset_layout.setContentsMargins(0, 5, 0, 0)
#             gps_offset_layout.setSpacing(5)

#             offset_title = QLabel("GPS Offset")
#             offset_title.setStyleSheet("font-size: 13px; font-weight: bold;")
            
#             # Safe Check: Fallback if parent data isn't configured yet
#             initial_offset = "+5:30"
#             if self.parent() and hasattr(self.parent(), 'gps_offset'):
#                 initial_offset = str(self.parent().gps_offset)
                
#             self.gps_offset = QLineEdit(initial_offset)
#             self.gps_offset.setFixedWidth(150)
#             self.gps_offset.setStyleSheet("background-color: white; color: black; border: 1px solid gray; padding: 4px; font-size: 13px;")
            
#             self.example_lbl = QLabel("e.g. +5:30")
#             self.example_lbl.setStyleSheet("color: #444444; font-size: 12px;")

#             gps_offset_layout.addWidget(offset_title)
#             gps_offset_layout.addWidget(self.gps_offset)
#             gps_offset_layout.addWidget(self.example_lbl)
            
#             mode_layout.addWidget(self.gps_offset_container)
           
          
#             mode_layout.addStretch() 
            
#             tabs.addTab(mode_tab, "Mode Selection")
#             self.avg_count_value = str(getattr(self.parent(), "avg_count", 4))
#             self.stray_limit_value = str(getattr(self.parent(), "stray_limit", 40))
#             # ------------------ TAB 2: Averaging ------------------
#             avg_tab = QWidget()
#             avg_layout = QVBoxLayout(avg_tab)
#             avg_layout.setContentsMargins(20, 10, 20, 10)
#             avg_layout.setSpacing(4)  # tight spacing between all widgets

#             avg_count_label = QLabel("Avg Count")
#             avg_count_label.setStyleSheet("font-size: 12px;")
#             avg_count_label.setContentsMargins(0, 0, 0, 0)

#             self.value_font = QFont("Courier New", 11)
#             self.avg_count = QComboBox()
#             self.avg_count.setStyleSheet("""
#             QComboBox {
#             background-color: #C0C0C0;          /* Gray container background */
#             border: 1px solid #808080;          /* Outer border */
#             padding: 4px;                       /* Inner spacing around the input */
#         }

#         /* White text entry area */
#         QComboBox QLineEdit {
#             background-color: white;
#             color: black;
#             border: 1px solid #A0A0A0;          
#             padding-left: 5px;
#             font-size:5px;
#         }

#         /* Square dropdown button on the right */
#         QComboBox::drop-down {
#             subcontrol-origin: padding;
#     subcontrol-position: top right;
#             width: 20px;
#     background-color: #DCDCDC;          /* Light gray button background */
#             border-left: 1px solid #A0A0A0;     
#             border-top-right-radius: 2px;
#             border-bottom-right-radius: 2px;
#             margin-top: 4px;                    
#             margin-bottom: 4px;
#             margin-right: 4px;
#                                         color:black;
                                        
#         }
#                                             QComboBox::down-arrow {
#             image: url(./image/arrow.down.svg);
#             width: 10px;
#             height: 10px;
#         }
#             """)
#             self.avg_count.setEditable(True)
#             self.avg_count.setFont(self.value_font)
#             self.avg_count.setFixedSize(170, 30)
#             self.avg_count.addItems([str(i) for i in range(1, 60)])
#             self.avg_count.setCurrentText(str(self.avg_count_value))

#             # Spacer between the two fields
#             spacer = QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

#             stray_count_label = QLabel("Stray Limit")
#             stray_count_label.setStyleSheet("font-size: 12px;")
#             stray_count_label.setContentsMargins(0, 0, 0, 0)

#             self.stray_limit = QComboBox()
#             self.stray_limit.setStyleSheet("""
#                 QComboBox {
#             background-color: #C0C0C0;          /* Gray container background */
#             border: 1px solid #808080;          /* Outer border */
#             padding: 4px;                       /* Inner spacing around the input */
#         }

#         /* White text entry area */
#         QComboBox QLineEdit {
#             background-color: white;
#             color: black;
#             border: 1px solid #A0A0A0;          
#             padding-left: 5px;
#             font-size:5px;
#         }

#         /* Square dropdown button on the right */
#         QComboBox::drop-down {
#             subcontrol-origin: padding;
#     subcontrol-position: top right;
#             width: 20px;
#     background-color: #DCDCDC;          /* Light gray button background */
#             border-left: 1px solid #A0A0A0;     
#             border-top-right-radius: 2px;
#             border-bottom-right-radius: 2px;
#             margin-top: 4px;                    
#             margin-bottom: 4px;
#             margin-right: 4px;
#                                         color:black;
                                        
#         }
#                                             QComboBox::down-arrow {
#             image: url(./image/arrow.down.svg);
#             width: 10px;
#             height: 10px;
#         }
#             """)
#             self.stray_limit.setEditable(True)
#             self.stray_limit.setFont(self.value_font)
#             self.stray_limit.setFixedSize(170, 30)
#             self.stray_limit.addItems([str(i) for i in range(0, 70)])
#             self.stray_limit.setCurrentText(str(self.stray_limit_value))

#             avg_layout.addWidget(avg_count_label)
#             avg_layout.addWidget(self.avg_count)
#             avg_layout.addSpacerItem(spacer)       # small gap between the two fields
#             avg_layout.addWidget(stray_count_label)
#             avg_layout.addWidget(self.stray_limit)
#             avg_layout.addStretch()                # pushes everything to top

#             tabs.addTab(avg_tab, "Averaging")
            
#             # ------------------ Bottom Row (Exit Button) ------------------
#             bottom_layout = QHBoxLayout()
#             bottom_layout.addStretch() 
            
#             exit_btn = QPushButton("Exit")
#             exit_btn.setFixedWidth(90)
#             exit_btn.setStyleSheet("""
#                 QPushButton { background-color: #cfcfcf; border: 1px solid #7c7c7c; padding: 6px 12px; font-weight: bold; }
#                 QPushButton:pressed { background-color: #9e9e9e; }
#             """)
#             exit_btn.clicked.connect(self.close)
#             bottom_layout.addWidget(exit_btn)
            
#             main_layout.addLayout(bottom_layout)

#             # ------------------ Signal & Initial State Assignments ------------------
        
#             self.dynamic_radio.blockSignals(True)

#             if self.parent() and hasattr(self.parent(), 'current_mode'):
#                 if self.parent().current_mode == "GYRO-LOG":
#                     self.dynamic_radio.setChecked(False)   # GYRO-LOG = checked
#                 else:
#                     self.dynamic_radio.setChecked(True)  # GPS = unchecked
#             else:
#                 self.dynamic_radio.setChecked(False)      # default: GPS

#             # 2. Refresh UI labels/visibility WITHOUT writing to parent
#             self._refresh_ui_only()

#             # 3. NOW connect signals — user changes after this point will write to parent
#             self.dynamic_radio.blockSignals(False)
#             self.dynamic_radio.toggled.connect(self.update_mode)
#             self.gps_offset.textChanged.connect(self.update_offset)
#             self.avg_count.currentTextChanged.connect(self.sync_averaging)
#             self.stray_limit.currentTextChanged.connect(self.sync_averaging)
        
#         def _refresh_ui_only(self):
#             """Update UI labels and visibility from current radio state — does NOT write to parent."""
#             if self.dynamic_radio.isChecked():
#                 self.dynamic_radio.setText("GYRO-LOG")
#                 self.textbox.setText("Select - GYRO-LOG")
#                 self.textbox2.setText("UnSelect - GPS")
#                 self.gps_offset_container.hide()
#             else:
#                 self.dynamic_radio.setText("GPS")
#                 self.textbox.setText("Select - GPS")
#                 self.textbox2.setText("UnSelect - GYRO-LOG")
#                 self.gps_offset_container.show()
            
#             # Sync the mode label display to match current parent state (read only)
#             if self.mode_lbl and self.parent() and hasattr(self.parent(), 'current_mode'):
#                 self.mode_lbl.setText(f"MODE {self.parent().current_mode}")
        
#         def update_offset(self, text):
#             try:
#                 if self.parent() and hasattr(self.parent(), 'gps_offset'):
#                     self.parent().gps_offset = text
#                     save_config(self)
#             except Exception as e:
#                 print(f"Offset Update Error: {e}")
#         def update_mode(self):
#             try:
#                 """Called ONLY when user physically toggles the radio button."""
#                 # First refresh the UI appearance
#                 self._refresh_ui_only()

#                 # NOW write to parent — user explicitly changed it
#                 if self.parent() and hasattr(self.parent(), 'current_mode'):
#                     if self.dynamic_radio.isChecked():
#                         self.parent().current_mode = "GPS"
#                     else:
#                         self.parent().current_mode = "GYRO-LOG"
#                 save_config(self)
            
#                 if self.mode_lbl:
#                     if self.dynamic_radio.isChecked():
#                         self.mode_lbl.setText("MODE GPS")
#                     else:
#                         self.mode_lbl.setText("MODE GYRO-LOG")
#             except Exception as e:
#                 print("Mode Update Error:", e)
    
    
       

#             if self.parent():

#                 self.parent().avg_count = int(self.avg_count.currentText())

#                 self.parent().stray_limit = int(self.stray_limit.currentText() )
#                 save_config(self)
#                 # Refresh highlight immediately
#                 if (hasattr(self.parent(), "pressure_dir_list")and self.parent().pressure_dir_list.isVisible()):
#                     self.parent().update_pressure_lists()
#         def sync_averaging(self):
#             try:
#                 if not self.parent():
#                     return

#                 avg_text = self.avg_count.currentText().strip()
#                 stray_text = self.stray_limit.currentText().strip()

#                 if not avg_text.isdigit() or not stray_text.isdigit():
#                     return

#                 self.parent().avg_count = int(avg_text)
#                 self.parent().stray_limit = int(stray_text)

#                 # <<< ADD THESE LINES >>>
#                 self.parent().rws_averager = WindAverager(
#                     self.parent().avg_count,
#                     self.parent().stray_limit
#                 )

#                 self.parent().rwd_averager = WindAverager(
#                     self.parent().avg_count,
#                     self.parent().stray_limit
#                 )
#                 # <<< END >>>

#                 save_config(self)

#                 if (
#                     hasattr(self.parent(), "pressure_dir_list")
#                     and self.parent().pressure_dir_list
#                     and self.parent().pressure_dir_list.isVisible()
#                 ):
#                     self.parent().update_pressure_lists()

#             except Exception as e:
#                 print(f"Averaging Error: {e}")
#         #16-7-26
#         # def sync_averaging(self):
#         #     try:
#         #         if not self.parent():
#         #             return

#         #         avg_text = self.avg_count.currentText().strip()
#         #         stray_text = self.stray_limit.currentText().strip()

#         #         if not avg_text.isdigit() or not stray_text.isdigit():
#         #             return

#         #         self.parent().avg_count = int(avg_text)
#         #         self.parent().stray_limit = int(stray_text)
                
#         #         save_config(self)

#         #         if (
#         #             hasattr(self.parent(), "pressure_dir_list")
#         #             and self.parent().pressure_dir_list
#         #             and self.parent().pressure_dir_list.isVisible()
#         #         ):
#         #             self.parent().update_pressure_lists()

#         #     except Exception as e:
#         #         print(f"Averaging Error: {e}")
from ui.common import *
from image import *
from Core.config_manager import save_config
class ConfigurationWindow(QDialog):
        def __init__(self, parent=None, mode_label=None):
            super().__init__(parent)
            self.mode_lbl = mode_label
            self.setWindowTitle("WSDS Configuration")
            self.setFixedSize(500, 500)
            self.setStyleSheet("background-color: #b3b3b3; color: black; font-family: Arial;")

            # Base layout for the entire Dialog window
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(15, 15, 15, 15)
            title = QLabel("WIND SPEED AND DIRECTION SYSTEM\nCONFIGURATION\nSensor & Mode selection")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("font-size: 18px; font-weight: bold;color:white;")
            main_layout.addWidget(title)

            # Main Tab Widget
            tabs = QTabWidget()
            tabs.setStyleSheet("""
                QTabWidget::pane { border: 1px solid #7c7c7c; background: #b3b3b3; }
                QTabBar::tab { background: #cfcfcf; color: black; padding: 8px 20px; margin-right: 2px; width:100px; }
                QTabBar::tab:selected { background: #b3b3b3; font-weight: bold; }
            """)
            main_layout.addWidget(tabs)

            # ------------------ TAB 1: Mode Selection ------------------
            mode_tab = QWidget()
            mode_layout = QHBoxLayout(mode_tab)
            
            mode_layout.setContentsMargins(20, 20, 20, 20)
            mode_layout.setSpacing(15)
            mode_group = QVBoxLayout()
            mode_group.setSpacing(8)
            

            # Right side - Sensor Selection
            sensor_group = QVBoxLayout()
            sensor_group.setSpacing(8)

            # Tab Title
            self.title_label = QLabel("Mode Selection")
         
            # self.title_label.setFixedWidth(100)
            self.title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            mode_group.addWidget(self.title_label)

            # Single Dynamic Radio Button
            self.dynamic_radio = QRadioButton()
            
            radio_style = """
                QRadioButton { color: black; font-size: 14px; }
                QRadioButton::indicator { width: 18px; height: 18px; }
                QRadioButton::indicator:unchecked { border: 2px solid #ababab; background-color: #f2f2f1; border-radius: 10px; }
                QRadioButton::indicator:checked { border: 2px solid #ababab; background-color: #f2f2f1; border-radius: 10px; }
            """
            self.dynamic_radio.setStyleSheet(radio_style)
            mode_group.addWidget(self.dynamic_radio)

            # Dynamic Status Labels
            self.textbox = QLabel()
            self.textbox2 = QLabel()
            self.textbox.setStyleSheet("font-size: 13px;")
            self.textbox2.setStyleSheet("font-size: 13px;")
            mode_group.addWidget(self.textbox)
            mode_group.addWidget(self.textbox2)

            # Container for GPS Offset elements (Hidden/Shown dynamically)
            self.gps_offset_container = QWidget()
            gps_offset_layout = QVBoxLayout(self.gps_offset_container)
            gps_offset_layout.setContentsMargins(0, 5, 0, 0)
            gps_offset_layout.setSpacing(5)

            offset_title = QLabel("GPS Offset")
            offset_title.setStyleSheet("font-size: 13px; font-weight: bold;")
            
            # Safe Check: Fallback if parent data isn't configured yet
            initial_offset = "+5:30"
            if self.parent() and hasattr(self.parent(), 'gps_offset'):
                initial_offset = str(self.parent().gps_offset)
                
            self.gps_offset = QLineEdit(initial_offset)
            self.gps_offset.setFixedWidth(150)
            self.gps_offset.setStyleSheet("background-color: white; color: black; border: 1px solid gray; padding: 4px; font-size: 13px;")
            
            self.example_lbl = QLabel("e.g. +5:30")
            self.example_lbl.setStyleSheet("color: #444444; font-size: 12px;")

            gps_offset_layout.addWidget(offset_title)
            gps_offset_layout.addWidget(self.gps_offset)
            gps_offset_layout.addWidget(self.example_lbl)
            
            mode_group.addWidget(self.gps_offset_container)
            mode_group.addStretch() 
            sensor_title = QLabel("Sensor Selection")
            sensor_title.setStyleSheet("font-size:14px;font-weight:bold;")
            sensor_group.addWidget(sensor_title)
            self.sensor_radio = QRadioButton()
            self.sensor_radio.setStyleSheet(radio_style)
            self.sensor_radio.setAutoExclusive(False)   # so it never gets fought over by siblings
            sensor_group.addWidget(self.sensor_radio)

            sensor_group.addSpacing(15)
            self.sensor_textbox = QLabel()
            self.sensor_textbox2 = QLabel()
            self.sensor_textbox.setStyleSheet("font-size: 13px;")
            self.sensor_textbox2.setStyleSheet("font-size: 13px;")
            sensor_group.addWidget(self.sensor_textbox)
            sensor_group.addWidget(self.sensor_textbox2)
            self.wind_sensor_container = QWidget()
            wind_sensor_Layout = QVBoxLayout(self.wind_sensor_container)
            wind_sensor_Layout.setContentsMargins(0, 5, 0, 0)
            wind_sensor_Layout.setSpacing(5)
            wind_lbl = QLabel("Wind Sensor")
            wind_lbl.setStyleSheet("font-size:13px;font-weight:bold;")
            self.wind_sensor = QComboBox()
            self.wind_sensor.setStyleSheet("""
                        QComboBox {
                        background-color: #C0C0C0;          /* Gray container background */
                        border: 1px solid #808080;          /* Outer border */
                        padding: 4px;                       /* Inner spacing around the input */
                    }
            
                    /* White text entry area */
                    QComboBox QLineEdit {
                        background-color: white;
                        color: black;
                        border: 1px solid #A0A0A0;          
                        padding-left: 5px;
                        font-size:5px;
                    }
            
                    /* Square dropdown button on the right */
                    QComboBox::drop-down {
                        subcontrol-origin: padding;
                subcontrol-position: top right;
                        width: 20px;
                background-color: #DCDCDC;          /* Light gray button background */
                        border-left: 1px solid #A0A0A0;     
                        border-top-right-radius: 2px;
                        border-bottom-right-radius: 2px;
                        margin-top: 4px;                    
                        margin-bottom: 4px;
                        margin-right: 4px;
                                                    color:black;
                                                    
                    }
                                                        QComboBox::down-arrow {
                        image: url(./image/arrow.down.svg);
                        width: 10px;
                        height: 10px;
                    }
                        """)
            self.wind_sensor.addItems(["PORT", "STBD"])
    
            self.wind_sensor.setFixedWidth(140)
            wind_sensor_Layout.addWidget(wind_lbl)
            wind_sensor_Layout.addWidget(self.wind_sensor)
            sensor_group.addWidget(self.wind_sensor_container)
            sensor_selection_radio=QHBoxLayout()
            self.sensor_port=QRadioButton("PORT")
            
            self.sensor_stbd=QRadioButton("STBD")
            indicator_style = """
                QRadioButton::indicator { width: 14px; height: 14px; border-radius: 7px; }
                QRadioButton::indicator:unchecked { background-color: #cfcfcf; border: 1px solid #7c7c7c; }
                QRadioButton::indicator:checked { background-color: #00cc00; border: 1px solid #007700; }
            """
            self.sensor_port.setStyleSheet(indicator_style)
            self.sensor_stbd.setStyleSheet(indicator_style)
            self.port_stbd_group = QButtonGroup(self)
            self.port_stbd_group.addButton(self.sensor_port)
            self.port_stbd_group.addButton(self.sensor_stbd)

            sensor_selection_radio.addWidget(self.sensor_port)
            sensor_selection_radio.addWidget(self.sensor_stbd)
            self.sensor_port.setChecked(True) 
            self.wind_sensor.currentIndexChanged.connect(self.on_index_changed)
            sensor_group.addLayout(sensor_selection_radio)   # <-- the actual layout goes here
            sensor_group.addStretch()
          
            mode_box = QGroupBox()
            mode_box.setFlat(True)
            mode_box.setLayout(mode_group)

            sensor_box = QGroupBox()
            sensor_box.setFlat(True)
            sensor_box.setLayout(sensor_group)

            mode_layout.addWidget(mode_box)
            mode_layout.addWidget(sensor_box)
            tabs.addTab(mode_tab, "Mode Selection")
            self.avg_count_value = str(getattr(self.parent(), "avg_count", 4))
            self.stray_limit_value = str(getattr(self.parent(), "stray_limit", 40))
            # ------------------ TAB 2: Averaging ------------------
            avg_tab = QWidget()
            avg_layout = QVBoxLayout(avg_tab)
            avg_layout.setContentsMargins(20, 10, 20, 10)
            avg_layout.setSpacing(4)  # tight spacing between all widgets

            avg_count_label = QLabel("Avg Count")
            avg_count_label.setStyleSheet("font-size: 12px;")
            avg_count_label.setContentsMargins(0, 0, 0, 0)

            self.value_font = QFont("Courier New", 11)
            self.avg_count = QComboBox()
            self.avg_count.setStyleSheet("""
            QComboBox {
            background-color: #C0C0C0;          /* Gray container background */
            border: 1px solid #808080;          /* Outer border */
            padding: 4px;                       /* Inner spacing around the input */
        }

        /* White text entry area */
        QComboBox QLineEdit {
            background-color: white;
            color: black;
            border: 1px solid #A0A0A0;          
            padding-left: 5px;
            font-size:5px;
        }

        /* Square dropdown button on the right */
        QComboBox::drop-down {
            subcontrol-origin: padding;
    subcontrol-position: top right;
            width: 20px;
    background-color: #DCDCDC;          /* Light gray button background */
            border-left: 1px solid #A0A0A0;     
            border-top-right-radius: 2px;
            border-bottom-right-radius: 2px;
            margin-top: 4px;                    
            margin-bottom: 4px;
            margin-right: 4px;
                                        color:black;
                                        
        }
                                            QComboBox::down-arrow {
            image: url(./image/arrow.down.svg);
            width: 10px;
            height: 10px;
        }
            """)
            self.avg_count.setEditable(True)
            self.avg_count.setFont(self.value_font)
            self.avg_count.setFixedSize(170, 30)
            self.avg_count.addItems([str(i) for i in range(1, 60)])
            self.avg_count.setCurrentText(str(self.avg_count_value))

            # Spacer between the two fields
            spacer = QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

            stray_count_label = QLabel("Stray Limit")
            stray_count_label.setStyleSheet("font-size: 12px;")
            stray_count_label.setContentsMargins(0, 0, 0, 0)

            self.stray_limit = QComboBox()
            self.stray_limit.setStyleSheet("""
                QComboBox {
            background-color: #C0C0C0;          /* Gray container background */
            border: 1px solid #808080;          /* Outer border */
            padding: 4px;                       /* Inner spacing around the input */
        }

        /* White text entry area */
        QComboBox QLineEdit {
            background-color: white;
            color: black;
            border: 1px solid #A0A0A0;          
            padding-left: 5px;
            font-size:5px;
        }

        /* Square dropdown button on the right */
        QComboBox::drop-down {
            subcontrol-origin: padding;
    subcontrol-position: top right;
            width: 20px;
    background-color: #DCDCDC;          /* Light gray button background */
            border-left: 1px solid #A0A0A0;     
            border-top-right-radius: 2px;
            border-bottom-right-radius: 2px;
            margin-top: 4px;                    
            margin-bottom: 4px;
            margin-right: 4px;
                                        color:black;
                                        
        }
                                            QComboBox::down-arrow {
            image: url(./image/arrow.down.svg);
            width: 10px;
            height: 10px;
        }
            """)
            self.stray_limit.setEditable(True)
            self.stray_limit.setFont(self.value_font)
            self.stray_limit.setFixedSize(170, 30)
            self.stray_limit.addItems([str(i) for i in range(0, 70)])
            self.stray_limit.setCurrentText(str(self.stray_limit_value))

            avg_layout.addWidget(avg_count_label)
            avg_layout.addWidget(self.avg_count)
            avg_layout.addSpacerItem(spacer)       # small gap between the two fields
            avg_layout.addWidget(stray_count_label)
            avg_layout.addWidget(self.stray_limit)
            avg_layout.addStretch()                # pushes everything to top

            tabs.addTab(avg_tab, "Averaging")
            
            # ------------------ Bottom Row (Exit Button) ------------------
            bottom_layout = QHBoxLayout()
            bottom_layout.addStretch() 
            
            exit_btn = QPushButton("Exit")
            exit_btn.setFixedWidth(90)
            exit_btn.setStyleSheet("""
                QPushButton { background-color: #cfcfcf; border: 1px solid #7c7c7c; padding: 6px 12px; font-weight: bold; }
                QPushButton:pressed { background-color: #9e9e9e; }
            """)
            exit_btn.clicked.connect(self.close)
            bottom_layout.addWidget(exit_btn)
            
            main_layout.addLayout(bottom_layout)

            # ------------------ Signal & Initial State Assignments ------------------
        
            self.dynamic_radio.blockSignals(True)

            if self.parent() and hasattr(self.parent(), 'current_mode'):
                if self.parent().current_mode == "GYRO-LOG":
                    self.dynamic_radio.setChecked(False)   # GYRO-LOG = checked
                else:
                    self.dynamic_radio.setChecked(True)  # GPS = unchecked
            else:
                self.dynamic_radio.setChecked(False)      # default: GPS
             # ------------------ Signal & Initial State Assignments ------------------

            # 2. Refresh UI labels/visibility WITHOUT writing to parent
            self._refresh_ui_only()

            # 3. NOW connect signals — user changes after this point will write to parent
            self.dynamic_radio.blockSignals(False)
            self.dynamic_radio.toggled.connect(self.update_mode)
            self.gps_offset.textChanged.connect(self.update_offset)
            self.avg_count.currentTextChanged.connect(self.sync_averaging)
            self.stray_limit.currentTextChanged.connect(self.sync_averaging)
            sensor_mode = getattr(self.parent(), "sensor_selection", "AUTO").upper()
            sensor_selected = getattr(self.parent(), "sensor_selected", "PORT").upper()

            self.sensor_radio.blockSignals(True)
            self.sensor_radio.setChecked(sensor_mode == "MANUAL")
            self.sensor_radio.blockSignals(False)

            self.wind_sensor.setCurrentText(
                    getattr(self.parent(), "sensor_selected", "PORT").upper()
            )

            self.refresh_sensor()

            # self.sensor_radio.blockSignals(False)
            self.sensor_radio.toggled.connect(self.update_sensor_mode)

        def on_index_changed(self, index):
            if index == 0:      # PORT
                self.sensor_port.setChecked(True)
            elif index == 1:    # STBD
                self.sensor_stbd.setChecked(True)
            if self.parent():
                self.parent().sensor_selected = self.wind_sensor.currentText().upper()

            save_config(self)
            


        def refresh_sensor(self):
                        """Update UI labels and visibility from current radio state — does NOT write to parent."""
                        if self.sensor_radio.isChecked():
                            self.sensor_radio.setText("Manual")
                            self.sensor_textbox.setText("Select - Manual")
                            self.sensor_textbox2.setText("UnSelect - Auto")
                            self.wind_sensor_container.show()
                     
                        else:
                            self.sensor_radio.setText("Auto")
                            self.sensor_textbox.setText("Select - Auto")
                            self.sensor_textbox2.setText("UnSelect - Manual")
                            self.wind_sensor_container.hide()
        def update_sensor_mode(self):
            try:
                self.refresh_sensor()

                if self.parent():
                    if self.sensor_radio.isChecked():
                        self.parent().sensor_selection = "MANUAL"
                    else:
                        self.parent().sensor_selection = "AUTO"

                print(self.parent().sensor_selection)
                save_config(self)

            except Exception as e:
                print("Mode Update Error:", e)

        def _refresh_ui_only(self):
            """Update UI labels and visibility from current radio state — does NOT write to parent."""
            if self.dynamic_radio.isChecked():
                self.dynamic_radio.setText("GYRO-LOG")
                self.textbox.setText("Select - GYRO-LOG")
                self.textbox2.setText("UnSelect - GPS")
                self.gps_offset_container.hide()
         
            else:
                self.dynamic_radio.setText("GPS")
                self.textbox.setText("Select - GPS")
                self.textbox2.setText("UnSelect - GYRO-LOG")
                self.gps_offset_container.show()
         
            
            # Sync the mode label display to match current parent state (read only)
            if self.mode_lbl and self.parent() and hasattr(self.parent(), 'current_mode'):
                self.mode_lbl.setText(f"MODE {self.parent().current_mode}")
        def update_offset(self, text):
            try:
                if self.parent() and hasattr(self.parent(), 'gps_offset'):
                    self.parent().gps_offset = text
                    save_config(self)
            except Exception as e:
                print(f"Offset Update Error: {e}")
        def update_mode(self):
            try:
                """Called ONLY when user physically toggles the radio button."""
                # First refresh the UI appearance
                self._refresh_ui_only()

                # NOW write to parent — user explicitly changed it
                if self.parent() and hasattr(self.parent(), 'current_mode'):
                    if self.dynamic_radio.isChecked():
                        self.parent().current_mode = "GPS"
                    else:
                        self.parent().current_mode = "GYRO-LOG"
                save_config(self)
            
                if self.mode_lbl:
                    if self.dynamic_radio.isChecked():
                        self.mode_lbl.setText("MODE GPS")
                    else:
                        self.mode_lbl.setText("MODE GYRO-LOG")
            except Exception as e:
                print("Mode Update Error:", e)
    
    
       

            if self.parent():

                self.parent().avg_count = int(self.avg_count.currentText())

                self.parent().stray_limit = int(self.stray_limit.currentText() )
                save_config(self)
                # Refresh highlight immediately
                if (hasattr(self.parent(), "pressure_dir_list")and self.parent().pressure_dir_list.isVisible()):
                    self.parent().update_pressure_lists()
       
      
       
        def sync_averaging(self):
            try:
                if not self.parent():
                    return

                avg_text = self.avg_count.currentText().strip()
                stray_text = self.stray_limit.currentText().strip()

                if not avg_text.isdigit() or not stray_text.isdigit():
                    return

                self.parent().avg_count = int(avg_text)
                self.parent().stray_limit = int(stray_text)
                
                save_config(self)

                if (
                    hasattr(self.parent(), "pressure_dir_list")
                    and self.parent().pressure_dir_list
                    and self.parent().pressure_dir_list.isVisible()
                ):
                    self.parent().update_pressure_lists()

            except Exception as e:
                print(f"Averaging Error: {e}")
        
