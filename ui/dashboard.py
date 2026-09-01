from Core.widgets import ClickableLabel, HoverLabel
from serialReader.serial_reader import SerialReader
from Core.wind_processor import process_wind_data
from Core.logger_manager import save_data_to_csv,init_log_file,finalize_log_file
from Core.config_manager import load_config
from ui.accessfile import unlock_file,lock_file
from Core.helper import safe_float, safe_int,format_nmea,safe_display,safe_display_cog,get_offset_time,validate_offset,log_value
from Core.status_manager import handle_status_label,update_all_blinking
from ui.common import *
from ui.maintenance import MaintenanceDialog
from ui.logviewer import LogViewer
from ui.configuration import ConfigurationWindow
import traceback
import ctypes
import logging

class Dashboard(QWidget):
    def __init__(self,fullscreen=False):
        super().__init__()
        if fullscreen:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint
            )

        self.spinbox_changed = False
        self.last_data_time = 0
        self.otswd_received = False
        self.last_otswd_time = time.time()
        # Timer to monitor OTSWD timeout
        self.data_monitor_timer = QTimer()
        self.data_monitor_timer.timeout.connect(self.check_otswd_timeout)
        self.data_monitor_timer.start(1000)   # check every 1 second
         
    
        self.sensor_headers = {}
        self.sensor_units = {}
        self.blink_state = False
        self.rel_wind_history = []
        self.serial_lock = threading.Lock()
        self.config_file = "config.json"
        load_config(self)
        self.log_dir = r"C:\WSDS DATA"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    # ── DELETE FILES OLDER THAN 6 MONTHS ─────────────────────────────
        # delete_old_logs(self)
        # self.enforce_folder_size_limit()
        LOG_MAX_SIZE_GB   = 30
        LOG_MAX_SIZE_BYTES = LOG_MAX_SIZE_GB * 1024 * 1024 * 1024  
    # ── CREATE NEW LOG FILE WITH .tdms EXTENSION ──────────────────────
        timestamp = datetime.datetime.now().strftime("%d-%b-%y %H-%M-%S")
        # self.current_log_file = os.path.join(self.log_dir, f"{timestamp}.tdms")
        self.current_log_file = os.path.join(self.log_dir, f"{timestamp}.awos")
        init_log_file(self)
        # 2. Write the header to the new file immediately

        self.setWindowTitle("Marine Electricals")
       
        self.setStyleSheet("background-color: black; color: white; font-family:Arial Black; ")
        self.last_raw_sentence = "No Data Received"
    
        self.sensor_values = {}
        self.is_night_mode = False
        # self.serial_thread = SerialReader()
        self.serial_thread = SerialReader(self.config_file)
        self.serial_thread.data_received.connect(self.update_data)
        self.serial_thread.raw_sentence_received.connect(self.update_raw_sentence)
        self.serial_thread.start()
        main_vbox = QVBoxLayout(self)
        main_vbox.setContentsMargins(5, 5, 5, 5)
        main_vbox.setSpacing(0) # Remove spacing between main sections
        top_hbox = QHBoxLayout()
        top_hbox.setSpacing(0) # Minimal line between panels
        # --- LEFT PANEL SETUP ---\
        left_panel = QFrame()
        left_panel.setFixedSize(260, 500)
        left_panel.setStyleSheet("border: 2px solid #acacac; background-color: black;")
        
        # Main Vertical Layout for the whole sidebar
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(10)
        
        # ====================================================
        # SOG BAR + COG VALUE AREA
        # ====================================================

        # Main Area Horizontal Layout
        sog_cog_area = QHBoxLayout()
        sog_cog_area.setContentsMargins(0, 0, 0, 0)
        sog_cog_area.setSpacing(10)

        # ----------------------------------------------------
        # Left Column: SOG Title + SOG Gauge 
        # ----------------------------------------------------
        sog_column = QVBoxLayout()
        sog_column.setContentsMargins(0, 0, 0, 0)
        sog_column.setSpacing(15)

        # SOG Header at the very top of the gauge
        self.sog_title = QLabel("SOG")
        self.sog_title.setStyleSheet("""
            color: white;
            border: none;
            font-family: 'Times New Roman';
            font-size: 30px;
            font-weight: bold;
            background: transparent;
        """)
        sog_column.addWidget(self.sog_title, alignment=Qt.AlignmentFlag.AlignLeft)

        # SOG Bar Chart Gauge
        self.sog_bar = LinearGauge()
        self.sog_bar.setFixedHeight(250)
        self.sog_bar.setFixedWidth(70)
        self.sog_bar.setStyleSheet("border: none; background: transparent;")
        sog_column.addWidget(self.sog_bar, alignment=Qt.AlignmentFlag.AlignBottom)
        
        sog_cog_area.addLayout(sog_column)

        # ----------------------------------------------------
        # Right Column: COG (Bordered Box) & SOG Kts Readout
        # ----------------------------------------------------
        right_panel_container = QWidget()
        right_panel_container.setStyleSheet("background: transparent; border: none;")
        
        right_layout = QVBoxLayout(right_panel_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # --- COG Box Frame (Left & Bottom Borders Only) ---
        cog_frame = QFrame()
        cog_frame.setMinimumWidth(180)
        cog_frame.setStyleSheet("""
            QFrame {
                border-left: 1px solid #ffffff;
                border-bottom: 1px solid #ffffff;
                border-top: none;
                border-right: none;
                background-color: transparent;
                width:120px;
            }
        """)
        
        cog_inner_layout = QVBoxLayout(cog_frame)
        cog_inner_layout.setContentsMargins(5, 0, 0, 0) 
        cog_inner_layout.setSpacing(5)

        # COG Title (Inside the frame, pushed to the top right)
        cog_header_layout = QHBoxLayout()
        cog_header_layout.setContentsMargins(15,0,0,0)
        # cog_header_layout.addStretch()
        self.cmg_title = QLabel("COG")
        self.cmg_title.setStyleSheet("""
            color: white;
            font-family: 'Times New Roman';
            font-size: 32px;
            font-weight: bold;
            border: none;
            background: transparent;
                                     
        """)
        cog_header_layout.addWidget(self.cmg_title)
        cog_inner_layout.addLayout(cog_header_layout)

        # COG Value ("48.4 deg")
        cog_value_layout = QHBoxLayout()
        cog_value_layout.setSpacing(4)
        # cog_value_layout.addStretch()
        
        self.deg_val = QLabel("248.40")
        
        self.deg_val.setStyleSheet("""
            color: white;
            font-size: 38px;
            font-family: 'Times New Roman';
            border: none;
            background: transparent;
        """)
        self.deg_val.setSizePolicy(
            QSizePolicy.Policy.Minimum, 
            QSizePolicy.Policy.Fixed
        )
        self.deg_val.adjustSize()
        self.deg_val_unit = QLabel("deg")
        self.deg_val_unit.setStyleSheet("""
            color: white; font-size: 20px; font-weight: bold; font-family: "Times New Roman"; border: none;padding: 0px; margin: 0px;line-height: 1;
        """)
        # self.deg_val = QLabel('<span style="font-family:\'Times New Roman\'; font-size:45px; color:white;">235.4</span>'
        #                       '<span style="font-family:\'Arial\'; font-size:20px; font-weight:bold; color:white;"> deg</span>')
        # self.deg_val.setStyleSheet("border: none; background: transparent;")
        
        cog_value_layout.addWidget(self.deg_val,Qt.AlignmentFlag.AlignBottom)
        cog_value_layout.addWidget(self.deg_val_unit,Qt.AlignmentFlag.AlignBottom)
        cog_inner_layout.addLayout(cog_value_layout)

        # Add the bordered COG block
        right_layout.addWidget(cog_frame)
        
        # Spacer pushes the SOG text layout down cleanly
        right_layout.addStretch()

        # --- SOG Numerical Value Layout (Outside the white border frame) ---
        sog_value_layout = QHBoxLayout()
        sog_value_layout.setContentsMargins(0, 0, 5, 5)
        sog_value_layout.setSpacing(5)
        sog_value_layout.addStretch()

        self.kts_val = QLabel("0.0")
        self.kts_val.setStyleSheet("""
            color: white;
            font-size: 38px;
            font-family: 'Times New Roman';
            border: none;
            background: transparent;
        """)

        self.kts_val_unit = QLabel("kts")
        self.kts_val_unit.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-family: 'Arial';
            font-weight: bold;
            border: none;
            background: transparent;
        """)

        sog_value_layout.addWidget(self.kts_val)
        sog_value_layout.addWidget(self.kts_val_unit)
        right_layout.addLayout(sog_value_layout)

        # Combine both columns back into the main view
        sog_cog_area.addWidget(right_panel_container, 1)
        left_layout.addLayout(sog_cog_area)
      
        coords_container = QVBoxLayout()
        coords_container.setSpacing(2)

        self.lat_lbl = QLabel("00000.00 N")
        self.long_lbl = QLabel("00000.00 E")
        self.time_lbl = QLabel("00:00:00")
        

        for lbl in [self.lat_lbl, self.long_lbl, self.time_lbl]:
            
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("""color: white; font-size: 29px;  font-family: "Arial"; border: none;padding: 0px; margin: 0px;line-height: 1; """)

        self.long_lbl.mousePressEvent = lambda e: self.stop_btn.setVisible(not self.stop_btn.isVisible())
        self.time_lbl.mousePressEvent = lambda e: self.maint_btn.setVisible(not self.maint_btn.isVisible())
       
        coords_container.addWidget(self.lat_lbl)
        coords_container.addWidget(self.long_lbl)
        coords_container.addWidget(self.time_lbl)
        left_layout.addLayout(coords_container)
        #   # # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_display)
        self.timer.start(1000)

        # 4. MODE AND NIGHT BUTTON
        left_layout.addStretch() # Pushes the button to the bottom
        self.mode_lbl = QLabel()

        self.mode_lbl.setText(
            f"<span style='font-family:\"Times New Roman\";'>MODE</span> "
            f"<span style='font-family:Arial;'>{self.current_mode}</span>"
        )

        self.mode_lbl.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.mode_lbl.setStyleSheet("color: white; border: none;")
        
        left_layout.addWidget(self.mode_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        left_layout.addStretch(1)
        self.night_btn = QPushButton("NIGHT")
        self.night_btn.setFixedSize(80, 40)
        
        self.night_btn.setStyleSheet("""
            QPushButton {background-color: #cccdcd; color: black;font-weight: bold;border: 1px solid #888;font-size:15px;}
            QPushButton:pressed { background-color: #333;} """)
        self.night_btn.clicked.connect(self.Night_btn_Clicked)
        left_layout.addWidget(self.night_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        top_hbox.addWidget(left_panel)
       
        # ================= RIGHT PANEL =================
        right_panel = QFrame()
        right_panel.setFixedHeight(500)
        right_panel.setStyleSheet("border: 2px solid #acacac;")

        # Create layout for right panel
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0,0,0,0)
        right_layout.setSpacing(0)
        # ================= HEADER =================
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(""" border-bottom: 2px solid #acacac; border-top: none; border-left: none; border-right: none; background-color: black;""")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(5, 5, 5, 5)

        company = QLabel("Marine Electricals")
        company.setStyleSheet("font-size: 30px; font-weight: bold; color: white; border: none; Font-family:Arial Black")
        logo = QLabel()
        # path = os.path.join(os.path.dirname(__file__), "image", "logo.png")
        path = os.path.join(os.path.dirname(__file__),"..","image","logo.png")

        print(path)
        print(os.path.exists(path))
        if os.path.exists(path):
            pixmap = QPixmap(path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio)
            logo.setPixmap(pixmap)

        header_layout.addStretch()
        header_layout.addWidget(company)
        header_layout.addStretch()
        header_layout.addWidget(logo)

        right_layout.addWidget(header)

        # ================= GAUGE SECTION =================
        gauge_layout = QHBoxLayout()
        rel_widget = QWidget()
        rel_widget.setFixedWidth(350)
        rel_widget.setStyleSheet("background-color:black; border:none;");

        # VERTICAL LAYOUT
        rel_layout = QVBoxLayout(rel_widget)

        # EVERYTHING CENTER
        rel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        rel_layout.setContentsMargins(0, 0, 0, 0)
        rel_layout.setSpacing(0)

        # ---------------- TITLE ----------------

        self.rel_title = QLabel("RELATIVE WIND")

        self.rel_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.rel_title.setStyleSheet("""
            QLabel{
                color:white;
                font-size:40px;
                font-family:"Times New Roman";
                font-weight:bold;
                border:none;
            
            }
        """)

        rel_layout.addWidget(
            self.rel_title,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        # ---------------- R LABEL ----------------

        self.r_label = QLabel("R")

        self.r_label.setFixedSize(35, 35)
       

        self.r_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.r_label.setStyleSheet("""
            QLabel{
                background-color:red;
                color:white;
                font-size:30px;
                font-weight:bold;
                border:2px solid #660000;
            }
        """)

        rel_layout.addWidget(
            self.r_label,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        # ---------------- GAUGE ----------------

        self.rel_gauge = NeedleGauge(mode="RG")
        self.rel_gauge.setStyleSheet("border:none; background:transparent;")
        rel_layout.addSpacing(-18)

    

        rel_layout.addWidget(
            self.rel_gauge,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        # ---------------- VALUE LAYOUT ----------------

        rel_value_layout = QHBoxLayout()
        rel_value_layout.setContentsMargins(0,0,0,20)
        rel_value_layout.setSpacing(0)

        rel_value_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ===== DEG =====

        deg_layout = QHBoxLayout()
        deg_layout.setSpacing(2)
        deg_layout.setContentsMargins(0, 0, 0, 0)
        deg_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.rel_box1 = QLabel("000.0")
        self.rel_box1.setFixedWidth(125)
        self.rel_box1.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.rel_box1.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 50px;
                font-family: "Times New Roman";
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)

        self.rel_box1Unit = QLabel("deg")
        self.rel_box1Unit.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 25px;
                font-family: "Times New Roman";
                border: none;
                padding: 0px;
                margin: 0px;
                font-weight:500;
                margin-bottom: 2px;   /* ← tweak this to align with number baseline */
            }
        """)
        self.rel_box1Unit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.rel_box1Unit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.rel_box1Unit.adjustSize()

        deg_layout.addWidget(self.rel_box1,     alignment=Qt.AlignmentFlag.AlignBottom)
        deg_layout.addWidget(self.rel_box1Unit, alignment=Qt.AlignmentFlag.AlignBottom)

        # ===== KTS =====

        kts_layout = QHBoxLayout()
        kts_layout.setSpacing(2)
        kts_layout.setContentsMargins(0, 0, 0, 0)
        kts_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)


        self.rel_box2 = QLabel("00.0")
        self.rel_box2.setFixedWidth(100)
        self.rel_box2.setAlignment(Qt.AlignmentFlag.AlignRight |Qt.AlignmentFlag.AlignBottom)
        self.rel_box2.setStyleSheet("""
            QLabel{
                color:white;
                font-size:50px;
                font-family:"Times New Roman";
                border:none;
            }
        """)

        self.rel_box2Unit = QLabel("kts")
        self.rel_box2Unit.setStyleSheet("""
            QLabel{
                color: white;
                font-weight:500;
                font-size: 25px;
                font-family: "Times New Roman";
                border: none;
                padding: 0px;
                margin: 0px;
                margin-bottom: 2px;   /* ← tweak this to align with number baseline */
            
            }
        """)
      
        self.rel_box2Unit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.rel_box2Unit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.rel_box2Unit.adjustSize()
        kts_layout.addWidget(self.rel_box2 ,alignment= Qt.AlignmentFlag.AlignBottom)
        kts_layout.addWidget(self.rel_box2Unit , alignment=Qt.AlignmentFlag.AlignBottom)
        
        # ADD BOTH
        rel_value_layout.addLayout(deg_layout)
        rel_value_layout.addLayout(kts_layout)

        rel_layout.addLayout(rel_value_layout)

        # =====================================================
        # TRUE WIND SECTION
        # =====================================================
        # ================= STOP BUTTON WIDGET =================

        stop_widget = QWidget()
        stop_widget.setFixedWidth(50)
        stop_widget.setStyleSheet("background:transparent; border:none;")
        stop_widget.setContentsMargins(0,50,0,0)
        stop_layout = QVBoxLayout(stop_widget)

        # CENTER BUTTON VERTICALLY
        stop_layout.addStretch()

        self.stop_btn = QPushButton("STOP")

        self.stop_btn.setFixedSize(45, 22)

        self.stop_btn.setStyleSheet("""
            QPushButton{
                background-color:#cbc5c4;
                color:red;
                font-weight:bold;
                border:1px solid #555;
                padding:0px;
            }
        """)

        self.stop_btn.hide()

        self.stop_btn.clicked.connect(self.close_application)

        stop_layout.addWidget(
            self.stop_btn,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        stop_layout.addStretch()
        
        true_widget = QWidget()
        true_widget.setStyleSheet("background-color:black; border:none;")

        true_layout = QVBoxLayout(true_widget)

        true_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        true_layout.setContentsMargins(0, 0, 0, 0)
        true_layout.setSpacing(0)

        # ---------------- TITLE ----------------

        self.true_title = QLabel("TRUE WIND")

        self.true_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.true_title.setStyleSheet("""
            QLabel{
                color:white;
                font-size:40px;
                font-family:"Times New Roman";
                font-weight:bold;
                border:none;
            }
        """)

        true_layout.addWidget(
            self.true_title,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        # EMPTY SPACE LIKE IMAGE
        spacer = QLabel("")
        spacer.setFixedHeight(32)

        true_layout.addWidget(
            spacer,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        # ---------------- GAUGE ----------------

        self.true_gauge = NeedleGauge(mode="white")

        # self.true_gauge.setFixedSize(280, 280)

        self.true_gauge.setStyleSheet("""
            border:none;
            background:transparent;
        """)
        true_layout.addSpacing(-18)
        true_layout.addWidget(
            self.true_gauge,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        # ---------------- VALUE LAYOUT ----------------

        true_value_layout = QHBoxLayout()
        true_value_layout.setContentsMargins(0,0,0,20)
        true_value_layout.setSpacing(0)

        true_value_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ===== DEG =====

        true_deg_layout = QHBoxLayout()
        true_deg_layout.setSpacing(2)
        true_deg_layout.setContentsMargins(0, 0, 0, 0)
        true_deg_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        # self.true_box1 = QLabel("000.0")
        self.true_box1 = HoverLabel("000.0")
        self.true_box1.setFixedWidth(125)
        self.true_box1.setAlignment(Qt.AlignmentFlag.AlignRight |Qt.AlignmentFlag.AlignBottom)

        self.true_box1.setStyleSheet("""
            QLabel{
                color:white;
                font-size:50px;
                font-family:"Times New Roman";
                border:none;
                padding: 0px;
                margin: 0px;                     
            }
        """)

        self.true_box1Unit = QLabel("deg")

        self.true_box1Unit.setStyleSheet("""
            QLabel{
                color:white;
                font-size:25px;
                font-family:"Times New Roman";
                border:none;
                padding-bottom:8px;
                          padding: 0px;
                margin: 0px;
                margin-bottom: 2px;  
                                         font-weight:500;              
            }
        """)
        self.true_box1Unit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.true_box1Unit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.true_box1Unit.adjustSize()

        true_deg_layout.addWidget(self.true_box1,alignment=Qt.AlignmentFlag.AlignBottom)
        true_deg_layout.addWidget(self.true_box1Unit,alignment=Qt.AlignmentFlag.AlignBottom)

        # ===== KTS =====

        true_kts_layout = QHBoxLayout()
        true_kts_layout.setSpacing(2)
        true_kts_layout.setContentsMargins(0, 0, 0, 0)
        true_kts_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.true_box2 = HoverLabel("00.0")
        self.true_box2.setFixedWidth(100)
        self.true_box2.setAlignment( Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        self.true_box2.setStyleSheet("""
            QLabel{
                color:white;
                font-size:50px;
                font-family:"Times New Roman";
                border:none;
            }
        """)

        self.true_box2Unit = QLabel("kts")

        self.true_box2Unit.setStyleSheet("""
            QLabel{
                color:white;
                font-size:25px;
                                         font-weight:500;
                font-family:"Times New Roman";
                border:none;
                  padding: 0px;
                margin: 0px;
                margin-bottom: 2px; 
            }
        """)
        self.true_box2Unit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.true_box2Unit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.true_box2Unit.adjustSize()

        true_kts_layout.addWidget(self.true_box2,alignment= Qt.AlignmentFlag.AlignBottom)
        true_kts_layout.addWidget(self.true_box2Unit,alignment= Qt.AlignmentFlag.AlignBottom)

        # ADD BOTH
        true_value_layout.addLayout(true_deg_layout)
        true_value_layout.addLayout(true_kts_layout)

        true_layout.addLayout(true_value_layout)


        # ================= STOP BUTTON WIDGET =================

        status_dot_widget = QWidget()
        status_dot_widget.setFixedWidth(50)
        status_dot_widget.setStyleSheet("background:transparent; border:none;")

        status_dot_layout = QVBoxLayout(status_dot_widget)

        # CENTER BUTTON VERTICALLY
        status_dot_layout.addStretch()

        self.status_dot = QLabel()
        self.status_dot.setFixedSize(16, 16)
        self.status_dot.setStyleSheet(
            "background-color: #00cc00;"
            "border-radius: 8px;"
            "border: 1px solid #006600;"
        )

        # self.stop_btn.hide()

        # self.stop_btn.clicked.connect(self.close_application)

        status_dot_layout.addWidget(
            self.status_dot,
            alignment=Qt.AlignmentFlag.AlignBottom| Qt.AlignmentFlag.AlignRight
        )
        self.miu_label = QLabel("Version: 0")
        self.miu_label.setStyleSheet(""" background-color: #cccdcd; color: black; font-size:14px;  padding:4px 10px; margin-right:25px;""")
        self.miu_label.setWindowFlags(Qt.WindowType.ToolTip)  # ✅ Floating top-level tooltip
        self.miu_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.miu_label.hide()
        self.mwvsentence = QLabel("  ")
        self.mwvsentence.setFixedWidth(170)
        self.mwvsentence.setStyleSheet(""" background-color: #cccdcd; color: black; font-size:12px;  padding:4px 10px; """)
        self.mwvsentence.setWindowFlags(Qt.WindowType.ToolTip)  # ✅ Floating top-level tooltip
        self.mwvsentence.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.mwvsentence.hide()
        # Timer for smooth hide (avoids flicker)
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.miu_label.hide)
        self.hide_timer.timeout.connect(self.mwvsentence.hide)


        # Connect hover signals
        self.true_box2.hovered.connect(self.show_miu)
        self.true_box2.left.connect(self.hide_miu)
        self.true_box1.hovered.connect(self.show_mwv)
        self.true_box1.left.connect(self.hide_mwv)
        stop_layout.addStretch()
        gauge_layout.addWidget(rel_widget)
        gauge_layout.addWidget(stop_widget)
        # gauge_layout.addWidget(self.stop_btn)
        gauge_layout.addWidget(true_widget)
        gauge_layout.addWidget(status_dot_widget)
        right_layout.addLayout(gauge_layout)
        
        top_hbox.addWidget(right_panel)
        main_vbox.addLayout(top_hbox)
        # --- 2. MIDDLE SECTION (Three Tiles - NO SPACING) ---
        tiles_hbox = QHBoxLayout()
        tiles_hbox.setSpacing(0) # THIS REMOVES THE GAP BETWEEN THE 3 TILES
        tiles_hbox.setContentsMargins(0, 0, 0, 0)
        self.sensor_values = {}  # store value labels here
        self.humidity_tile = self.create_sensor_tile("Relative<br> Humidity", "0.0", "%")
        tiles_hbox.addWidget(self.humidity_tile)
        tiles_hbox.addWidget(self.create_sensor_tile("Temperature", "0.0", "°C","Dew Point", "0.0", "°C"))
        tiles_hbox.addWidget(self.create_sensor_tile("Pressure", "0.0", "mBar"))
        # tiles_hbox.addWidget(self.create_sensor_tile("Visibility", "0.0", "m") )

        main_vbox.addLayout(tiles_hbox)
   
        tiles_hbox = QHBoxLayout()
        tiles_hbox.setSpacing(0)
        tiles_hbox.setContentsMargins(0, 0, 0, 0)
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(50)
        bottom_bar.setStyleSheet("border: 2px solid #acacac; border-top: none;")
        btn_lay = QHBoxLayout(bottom_bar)
        btn_lay.setContentsMargins(10, 0, 10, 0)
        label_style = """QLabel {background-color: yellow;color: red;font-weight: bold;font-size: 12px;border: 1px solid black;padding: 5px;qproperty-alignment: AlignCenter; height:10px;margin:10px 0px 10px 0px;}"""
        self.WSS = QLabel("WS S")
        self.WSS.setStyleSheet(label_style)  
        self.WSP = QLabel("WS P")
        self.WSP.setStyleSheet(label_style)
        self.Gyro = QLabel("GYRO")
        self.Gyro.setStyleSheet(label_style)
        
        self.Log = QLabel("LOG")
        self.Log.setStyleSheet(label_style)
       
        self.GPS = QLabel("GPS")
        self.GPS.setStyleSheet(label_style)
       
        self.HT = QLabel("H-T")
        self.HT.setStyleSheet(label_style)
        self.pres_label = QLabel("PRES")
        self.pres_label.setStyleSheet(label_style)
        
        self.visi = QLabel("VISI")
        self.visi.setStyleSheet(label_style)
        self.blink_flags = {
        "WSP": False,
        "WSS": False,
        "GYRO": False,
        "GPS": False,
        "LOG": False,
        "HUMIDITY": False,
        "PRESSURE": False,
        "VISIBILITY": False
        }

        self.blink_labels = {
            "WSP": self.WSP,
            "WSS": self.WSS,
            "GYRO": self.Gyro,
            "GPS": self.GPS,
            "LOG": self.Log,
            "HUMIDITY": self.HT,
            "PRESSURE": self.pres_label,
            "VISIBILITY": self.visi
        }
        hidden_style = """color: transparent;background-color: transparent;border: none;"""

        for lbl in self.blink_labels.values():
            lbl.setStyleSheet(hidden_style)

        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(lambda: update_all_blinking(self))
        self.blink_timer.start(500)

        self.maint_btn = QPushButton("MAINTENANCE")
        # self.maint_btn.setFixedSize(120, 30)
        self.maint_btn.setStyleSheet("padding:3px; background-color: #cccdcd; border: 1px solid #888; color:black;font-weight:bold;font-size:15px;")
        self.maint_btn.hide()
        self.maint_btn.clicked.connect(self.open_maintenance)

        self.btn_view_log = QPushButton("VIEW LOG")
        self.btn_view_log.clicked.connect(self.open_log_viewer)
        self.btn_config = QPushButton("CONFIGURE")
        self.btn_config.clicked.connect(self.open_Config)

        # Styling buttons
        btn_style = "padding:3px; background-color: #cccdcd; border: 1px solid #888; color:black;font-weight:bold;font-size:15px;"
        
        self.btn_view_log.setStyleSheet(btn_style)
        self.btn_config.setStyleSheet(btn_style)
        btn_lay.addWidget(self.WSS)
        btn_lay.addWidget(self.WSP)
        btn_lay.addWidget(self.Gyro)
        btn_lay.addWidget(self.Log)
        btn_lay.addWidget(self.GPS)
        btn_lay.addWidget(self.HT)
        btn_lay.addWidget(self.pres_label)
        btn_lay.addWidget(self.visi)
        # btn_lay.addWidget(self.stop_btn)
        btn_lay.addStretch() # Pushes maintenance to left, others to right
        btn_lay.addWidget(self.maint_btn)
        btn_lay.addWidget(self.btn_view_log)
        btn_lay.addWidget(self.btn_config)

        main_vbox.addWidget(bottom_bar)
        
        # Add a final stretch so everything stays pushed to the top
        main_vbox.addStretch()
        self.night_widgets = [self.long_lbl,self.lat_lbl,self.rel_box1,self.rel_box2,self.true_box1,self.true_box2,
        self.deg_val,
        self.kts_val
        ]
        # self.is_night_mode = True
        self.clear_all_fields()

   
    def update_time_display(self):

        if hasattr(self, 'latest_gps_time') and self.latest_gps_time:

            try:
                gps_time = str(self.latest_gps_time).strip().upper()
                # if not validate_offset(self,gps_time):
                #     return
                # INVALID VALUES
                if gps_time in ["", "---", "INF", "NONE"]:
                    # offset = self.gps_offset.lstrip("+-")  # Remove + or -
                    # hours, minutes = map(int, offset.split(":"))

                    # self.time_lbl.setText(f"{hours:02d}:{minutes:02d}:00")
                    offset = self.gps_offset.strip()

                    if offset.startswith("+"):
                        hours, minutes = map(int, offset[1:].split(":"))
                        result = timedelta(hours=hours, minutes=minutes)
                    else:
                        hours, minutes = map(int, offset[1:].split(":"))
                        result = timedelta(hours=24, minutes=0) - timedelta(hours=hours, minutes=minutes)

                    total_seconds = int(result.total_seconds())
                    h = total_seconds // 3600
                    m = (total_seconds % 3600) // 60
                    s = total_seconds % 60

                    self.time_lbl.setText(f"{h:02d}:{m:02d}:{s:02d}")
                    # self.time_lbl.setText(datetime.datetime.strptime(self.gps_offset, "%H%M%S.%f"))
                    return

                new_time = get_offset_time(self,gps_time, self.gps_offset)

                self.time_lbl.setText(new_time)

            except Exception as e:
                print(f"Time Display Error: {e}")
                self.time_lbl.setText("--:--:--")

    def check_otswd_timeout(self):

        if time.time() - self.last_otswd_time > 2:

            if self.otswd_received:   # avoid repeated clearing
                self.clear_all_fields()

            self.otswd_received = False
            # self.last_raw_sentence = "NO DATA RECEIVED"
            
            if (
                hasattr(self, "maintenance_dialog")
                and self.maintenance_dialog
                and self.maintenance_dialog.isVisible()
            ):
                self.maintenance_dialog.update_sentence("NO DATA RECEIVED")
            self.update_true_wind_status(False)
   
    def clear_all_fields(self):

        # Relative Wind
        self.rel_box1.setText("")
        self.rel_box2.setText("")
        self.rel_gauge.setAngle(0)

        # True Wind
        self.true_box1.setText("")
        self.true_box2.setText("")
        self.true_gauge.setAngle(0)

        # GPS / SOG / CMG
        self.lat_lbl.setText(".")
        self.long_lbl.setText(".")
        self.deg_val.setText("")
        self.kts_val.setText("")
        self.time_lbl.setText("00:00:00")

        # Sensor values
        for key in self.sensor_values:
            self.sensor_values[key].setText(".")

        
        self.sog_bar.set_value("")

       
        for key in self.blink_flags:
            self.blink_flags[key] = False
    def update_data(self, data):
        try:
            self.last_data_time = time.time()
            self.update_true_wind_status(True)
        # Format Latitude & Longitude
            lat_val = data['latitude']
            lat_val = str(data['latitude']).strip().upper()
            if "INF" in lat_val:
                lat = "INF"
            else:
                
                lat = f"{lat_val[:2]}° {lat_val[2:]}' {data['ns']}"

            long_val = str(data['longitude']).strip().upper()
            if "INF" in long_val:
                lon = "INF"
            else:
                lon = f"{long_val[:3]}° {long_val[3:]}' {data['ew']}"
            humidity=f"{data['humidity']}"
            Tempture=f"{data['Temp']}"
            dewPoint=f"{data['dewP']}"
            Pressure=f"{data['Pressure']}"
            visibility=f"{data['visibility']}"
            gps_time=f"{data['gps_time']}"
            
            MIU=f"{data['MIU']}"
            RWA=f"{data['RelativeWindAddress']}"
            
            rwd1 = safe_float(data.get('RelativeWindDirection1'))
            rwd2 = safe_float(data.get('RelativeWindDirection2'))

            rws1 = safe_float(data.get('RelativeWindSpeed1'))
            rws2 = safe_float(data.get('RelativeWindSpeed2'))
           
            time_lbl1=f"{data['gps_time']}"
            self.latest_gps_time = gps_time

           
            SOG = float(data.get('SOG', 0))
           

           
            CMG = float(data.get('CMG', 0))
            
            log_raw = str(data.get('log', '')).strip().upper()

            if log_raw in ["INF", "+INF", "-INF"]:
                log = float("inf")
            else:
                try:
                    log = float(log_raw)
                except:
                    log = 0.0
            try:
                heading = float(data.get('heading', 0))
            except:
                heading = 0.0


            if "Relative<br> Humidity" in self.sensor_values:
                hum=safe_display(self,humidity)
                humi=humidity
                self.sensor_values["Relative<br> Humidity"].setText(
                    f"{hum}"
                )

            if "Temperature" in self.sensor_values:
                temp=safe_display(self,Tempture)
                tempi=Tempture
                self.sensor_values["Temperature"].setText(
                    f"{temp}"
                )

            if "Dew Point" in self.sensor_values:
                dp=safe_display(self,dewPoint)
                dpi=dewPoint
                self.sensor_values["Dew Point"].setText(
                    f"<span style='font-size:44px'>{dp}</span>"
                )

            if "Pressure" in self.sensor_values:
                pressure = safe_display(self,Pressure)
                pressurei=Pressure
                self.sensor_values["Pressure"].setText(
                    f"{pressure}"
                )

            # if "Visibility" in self.sensor_values:
            #     vis = safe_display(self,visibility)
            #     visii=visibility
            #     self.sensor_values["Visibility"].setText(
            #         f"{vis}"
            #     )


         
            MIUV = MIU.split("*")
            
            self.miu_label.setText(f'AWOS MFCR v5.0 {MIUV[0]}')
          

           
            self.latest_gps_time = gps_time

            # Process wind
            selected_rws, selected_rwd, avg_rws, avg_rwd, tws, twa = process_wind_data(self,
                rws1, rws2, rwd1, rwd2, log, SOG,heading,CMG
            )
            
            relDir = ""
            if avg_rwd is None:
                self.rel_box1.setText("")
                self.rel_gauge.setAngle(0)
                
            else:
                self.rel_gauge.setAngle(avg_rwd)
                if avg_rwd >180:
                    relDir=360-avg_rwd
                    self.r_label.setText("R")
                    self.r_label.setStyleSheet("background-color: red; color: white;font-weight: bold; font-size: 30px; border:none; text-align:center;margin-left:10px;")

                    self.rel_box1.setText(f"{relDir:.1f}")
                    
                else:
                    relDir = round(avg_rwd, 1)
                    if self.is_night_mode:
                        g_color = "#00e3b8"      # Night color
                    else:
                        g_color = "green"  
                    self.r_label.setText("G")
                    self.r_label.setStyleSheet(f"""background-color: {g_color}; color: white;font-weight: bold; font-size: 30px; border:none; text-align:center;margin-left:10px;""")

                    self.rel_box1.setText(f"{relDir:.1f}")
                
            relSpd="" 
            # RELATIVE WIND SPEED
            if avg_rws is None:
                self.rel_box2.setText("")
            else:
                relSpd= round(avg_rws, 1)
                self.rel_box2.setText(f"{relSpd:.1f}")

            tRel=""
            # TRUE WIND DIRECTION
            if twa is None:
                self.true_box1.setText("")
                self.true_gauge.setAngle(0)
            else:
                tRel=round(twa,1)
                self.true_box1.setText(f"{tRel:.1f}")
                self.true_gauge.setAngle(twa)
            tSpd=""
            # TRUE WIND SPEED
            if tws is None:
                self.true_box2.setText("")
            else:
                tSpd=round(tws,1)
                self.true_box2.setText(f"{tSpd:.1f}")
            
        # Format Time
            self.lat_lbl.setText(lat)
            self.long_lbl.setText(lon)

            # self.deg_val.setText(f"{CMG:>7}")
            # # self.kts_val.setText(safe_display(self,SOG))
            # self.kts_val.setText(f"{SOG:>7}")

            self.deg_val.setText(safe_display_cog(self, CMG))
            self.kts_val.setText(safe_display(self,SOG))
            try:
            # Convert string to float for the gauge logic
                sog_value = float(SOG)
                self.sog_bar.set_value(sog_value) # Use setValue or set depending on your LinearGauge class
            except ValueError:
           
                self.sog_bar.set_value(0.0)
            
            
            
 
            if self.master_slave.upper() == "MASTER":

                try:
                    avg_rwd_str=f"{avg_rwd:.1f}" if avg_rwd is not None else ""
                    avg_rws_str=f"{avg_rws:.1f}" if avg_rws is not None else ""
                    mwv_sent = format_nmea(self,
                        f"WIMWV,{avg_rwd_str},R,{avg_rws_str},N,A"
                    )
                    self.mwvsentence.setText(f"WIMWV,{avg_rwd_str},R,{avg_rws_str},N,A")
                    
                    # mwd_sent = format_nmea(self,
                    #     f"WIMWD,{twa:.1f},T,{twa:.1f},M,{tws:.1f},N,{tws*0.51444:.1f},M"
                    # )
                    twa_str = f"{twa:.1f}" if twa is not None else ""
                    tws_str = f"{tws:.1f}" if tws is not None else ""
                    tws_ms = f"{tws*0.51444:.1f}" if tws is not None else ""

                    mwd_content = f"WIMWD,{twa_str},T,{twa_str},M,{tws_str},N,{tws_ms},M"
                    mwd_sent =format_nmea(self,mwd_content)
                    
                    xdr_content = f"WIXDR,C,{temp},C,1,H,{hum},P,2,P,{pressure},P,3,C,{dp},C,4,D,,M,5"

                    xdr_sent =format_nmea(self,xdr_content)

                    try:
                        with self.serial_lock:

                            if (
                                hasattr(self.serial_thread, 'serial_port')
                                and self.serial_thread.serial_port.is_open
                            ):

                                for sentence in [mwv_sent, mwd_sent,xdr_sent,]:
                                    self.serial_thread.serial_port.write(
                                        sentence.encode('ascii')
                                    )
                                    self.serial_thread.serial_port.flush()

                    except Exception as e:
                        print(f"Failed to send: {e}")

                except Exception as e:
                    print(f"NMEA Output Error: {e}")

           # ---- STATUS HANDLING ----
            handle_status_label(self,"WSP", data.get("RelativeWindSpeed1"))
            handle_status_label(self,"WSS", data.get("RelativeWindSpeed2"))
            handle_status_label(self,"GYRO", data.get("heading"))
            handle_status_label(self,"GPS", data.get("gps_time"))
            handle_status_label(self,"LOG", data.get("log"))
            handle_status_label(self,"HUMIDITY", data.get("humidity"))
            handle_status_label(self,"PRESSURE", data.get("Pressure"))
            handle_status_label(self,"VISIBILITY", data.get("visibility"))
            # tbl_model_text = self.mode_lbl.text()
            plain_text = re.sub(r'<[^>]+>', '', self.mode_lbl.text()).strip()
            tbl_model_text = plain_text.split()[-1]
            sensor_selection = self.sensor_selection
            sensor_selected = self.sensor_selected
            

            now = datetime.datetime.now()
            sys_date = now.strftime("%Y-%m-%d")
            sys_time = now.strftime("%H:%M:%S")
            # gps_time =gps_time
            gps_time = self.time_lbl.text()
            # Sensor1_Dir=rwd1
            # Sensor1_spd=rws1
            # Sensor2_Dir=rwd2
            # Sensor2_spd=rws2
            Sensor1_Dir = "INF" if math.isinf(rwd1) else rwd1
            Sensor1_spd = "INF" if math.isinf(rws1) else rws1
            Sensor2_Dir = "INF" if math.isinf(rwd2) else rwd2
            Sensor2_spd = "INF" if math.isinf(rws2) else rws2
            
            rel_dir = f"{avg_rwd:.2f}" if avg_rwd is not None else ""
            rel_speed = f"{avg_rws:.2f}" if avg_rws is not None else ""
            true_dir = tRel
            true_speed = tSpd
            cmg = "INF" if math.isinf(CMG) else CMG
            sog = "INF" if math.isinf(SOG) else SOG
            log_val = "INF" if math.isinf(log) else log
            gyro_val = "INF" if math.isinf(heading) else heading
            mode=tbl_model_text
            sensor_selection=sensor_selection
            sensor_selected=sensor_selected
            lat=lat
            long=lon
            Humidity=humi
            Tempture=tempi
            DewPoint=dpi
            Pressure=pressurei
            visibility=""
            # Avg_Dir=avg_rwd
            # Avg_speed=avg_rwd
            avg_count = self.avg_count[0] if isinstance(self.avg_count, tuple) else self.avg_count
            stray_limit = self.stray_limit[0] if isinstance(self.stray_limit, tuple) else self.stray_limit


          
            # 3. Create the list in the EXACT order of your headers
            data_row = [sys_date,sys_time,gps_time,Sensor1_Dir,Sensor1_spd,Sensor2_Dir,Sensor2_spd,rel_dir,rel_speed,true_dir,true_speed,cmg,sog,log_val,gyro_val,mode,sensor_selection,sensor_selected,lat,long,Humidity,DewPoint,Tempture,Pressure,visibility,avg_count,stray_limit]
            save_data_to_csv(self,data_row)  
        except Exception as e:
            print(f"update_data Error: {e}")
            traceback.print_exc()           
    

    def update_true_wind_status(self, is_ok):
        if is_ok:
            self.status_dot.setStyleSheet("background-color: #00cc00;""border-radius: 8px;""border: 1px solid #006600;")
        else:
            self.status_dot.setStyleSheet("background-color: #EE4B2B;" "border-radius: 8px;" "border: 1px solid #EE4B2B;")
            
    def close_application(self):
        QTimer.singleShot(3000, self.close) 

    def show_miu(self):
        self.hide_timer.stop()
    
        text = self.miu_label.text()  # already updated in update_data()
        self.miu_label.setText(text)
        self.miu_label.adjustSize()  # ✅ important

        # Get global position of true_box2
        pos = self.true_box2.mapToGlobal(self.true_box2.rect().topLeft())
        
        # Center tooltip above true_box2
        x = pos.x() + (self.true_box2.width() - self.miu_label.width()) // 2
        y = pos.y() - self.miu_label.height() + 110
        self.miu_label.move(x, y)
        self.miu_label.show()

    def hide_miu(self):
        self.hide_timer.start(200)  # short delay to avoid flicker


    def show_mwv(self):
        self.hide_timer.stop()
    
        text = self.mwvsentence.text()  # already updated in update_data()
        self.mwvsentence.setText(text)
        self.mwvsentence.adjustSize()  # ✅ important

        # Get global position of true_box2
        pos = self.true_box1.mapToGlobal(self.true_box1.rect().topLeft())
        
        # Center tooltip above true_box2
        x = pos.x() + (self.true_box1.width() - self.mwvsentence.width()) // 2
        y = pos.y() - self.mwvsentence.height() + 110
        self.mwvsentence.move(x, y)
        self.mwvsentence.show()

    def hide_mwv(self):
        self.hide_timer.start(200)  # short delay to avoid flicker
    def open_maintenance(self):
        try:
            if hasattr(self, "maintenance_dialog") and self.maintenance_dialog.isVisible():
                self.maintenance_dialog.raise_()
                self.maintenance_dialog.activateWindow()
                return

            sentence = self.last_raw_sentence or "NO DATA RECEIVED"

            self.maintenance_dialog = MaintenanceDialog(sentence, self)
            self.maintenance_dialog.show()      # <-- use show() instead of exec()

        except Exception as e:
            print(f"Open Maintenance Error: {e}")
    # def open_maintenance(self):
    #     try:

    #         if (
    #             not self.last_raw_sentence
    #             or self.last_raw_sentence == "NO DATA RECEIVED"
    #         ):
    #             sentence = "NO DATA RECEIVED"
    #         else:
    #             sentence = self.last_raw_sentence

    #         dlg = MaintenanceDialog(sentence, self)
    #         dlg.exec()

    #     except Exception as e:
    #         print(f"Open Maintenance Error: {e}")
    #         traceback.print_exc()

    def update_raw_sentence(self, sentence):

        self.last_raw_sentence = sentence
        self.last_otswd_time = time.time()
        raw = sentence.strip().upper()

        # Detect OTSWD sentence
        if "$OTSWD" in raw:

            self.otswd_received = True
            # self.last_otswd_time = time.time()
        if (
            hasattr(self, "maintenance_dialog")
            and self.maintenance_dialog
            and self.maintenance_dialog.isVisible()
        ):
            sentence = self.last_raw_sentence or "NO DATA RECEIVED"
            self.maintenance_dialog.update_sentence(sentence)
    
    def pressure_clicked(self):
        visible = not self.pressure_dir_list.isVisible()

        if visible:
            # 1. Populate the data rows first so the widget calculates its layout items
            self.update_pressure_lists()
            
            # 2. Get screen position of the target Relative Humidity tile
            humidity_pos = self.humidity_tile.mapTo(self, self.humidity_tile.rect().topLeft())
            tile_width = self.humidity_tile.width()
            
            # 3. Use an explicit height fallback (18px per item * 8 items + borders = ~150px)
            # This fixes the "initially blank/invisible" geometry bug
            list_height = self.pressure_dir_list.height()
            if list_height <= 0:
                list_height = 150 

            # 4. Calculate floating coordinates directly above the humidity tile
            list_y = humidity_pos.y() - list_height + 150  # 10px padding above tile
            dir_x = humidity_pos.x() + int((tile_width / 2) - 65)
            speed_x = humidity_pos.x() + int((tile_width / 2) + 195)
            
            # 5. Reposition lists
            self.pressure_dir_list.move(dir_x, list_y)
            self.pressure_speed_list.move(speed_x, list_y)
            
            # 6. Reposition accompanying spinboxes underneath their respective lists
            self.spinbox.move(dir_x - 45, list_y + list_height - 115)
            self.spinbox1.move(speed_x - 45, list_y + list_height -115)
            
            # 7. Bring elements to front layer context
            self.pressure_dir_list.raise_()
            self.pressure_speed_list.raise_()
            self.spinbox.raise_()
            self.spinbox1.raise_()

        # 8. Set visibility states cleanly
        self.pressure_dir_list.setVisible(visible)
        self.pressure_speed_list.setVisible(visible)
        self.spinbox.setVisible(visible)
        self.spinbox.valueChanged.connect(self.on_spinbox_changed)
        self.spinbox1.setVisible(visible)

    def on_spinbox_changed(self):
        self.spinbox_changed = True
        self.update_pressure_lists()
    def update_pressure_lists(self):
        if not hasattr(self, 'rel_wind_history'):
            return

        self.pressure_dir_list.clear()
        self.pressure_speed_list.clear()

        MAX_ROWS = 8
        
        try:
            avg_count = int(self.avg_count)
        except (AttributeError, ValueError):
            avg_count = 0
            
        print("CURRENT AVG COUNT =", avg_count)
        
        # Pull history (latest values at index 0)
        history = getattr(self, 'rel_wind_history', [])[::-1][:MAX_ROWS]

        for i in range(MAX_ROWS):
            # if i < len(history):
            #     direction, stray = history[i]
            #     dir_text = f"{direction}" if not str(direction).endswith('°') else str(direction)
            #     speed_text = f"{stray}" if float(stray) >= 0 else str(stray)
            # else:
            #     dir_text = "0"
            #     speed_text = "0"
            if i < len(history):
                direction, stray = history[i]

                # Direction: show only avg_count rows
                if i < avg_count:
                    dir_text = str(direction)
                else:
                    dir_text = "0"

                # Speed: always show actual value
                speed_text = str(stray)

            else:
                dir_text = "0"
                speed_text = "0"

            # 1. Row item size definitions
            dir_item = QListWidgetItem()
            speed_item = QListWidgetItem()
            dir_item.setSizeHint(QSize(60, 18))
            speed_item.setSizeHint(QSize(60, 18))

            # 2. TOP-DOWN COUNT LOGIC FIXED HERE
            # If i is less than avg_count, it falls inside the active calculation zone
            # highlight_count = self.spinbox.value()
            if self.spinbox_changed:
                highlight_count = self.spinbox.value()
            else:
                highlight_count = avg_count

            invalid_selection = highlight_count > avg_count
            # if i < avg_count:
            #     bg = "#b0b0b0"  # Jet black background for active items
            #     fg = "white"  # Bold red text color for active items (Image 2)
            # else:
            #     bg = "#5a5a5a"  # Gray background canvas for inactive tracking logs
            #     fg = "white"  # Crisp white text color for standby data
            # highlight_count = self.spinbox.value()

            # if highlight_count > avg_count:
            #     dir_text = "0"
            #     bg = "#5a5a5a"
            #     fg = "white"

            # else:
            #     if i < highlight_count and i < len(history):
            #         direction, stray = history[i]
            #         dir_text = str(direction)
            #         bg = "#b0b0b0"      # light gray
            #         fg = "white"
            #     else:
            #         dir_text = "0"
            #         bg = "#5a5a5a"      # dark gray
            #         fg = "white"
            if invalid_selection:
                dir_text = "0"
                bg = "#5a5a5a"
                fg = "white"

            else:

                if i < len(history):
                    direction, stray = history[i]

                    if i < highlight_count:
                        dir_text = str(direction)
                        bg = "#b0b0b0"      # light gray
                    else:
                        dir_text = "0"
                        bg = "#5a5a5a"      # dark gray

                    fg = "white"
                    speed_text = str(stray)

                else:
                    dir_text = "0"
                    speed_text = "0"
                    bg = "#5a5a5a"
                    fg = "white"

            # 3. Custom Container Widget: Direction Column
            dir_frame = QFrame()
            dir_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg};
                    border-bottom: 1px solid #222222;
                }}
                QLabel {{
                    color: {fg};
                    font-size: 12px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }}
            """)
            dir_layout = QHBoxLayout(dir_frame)
            dir_layout.setContentsMargins(0, 0, 0, 0)
            dir_layout.setSpacing(0)
            
            dir_label = QLabel(dir_text)
            dir_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dir_layout.addWidget(dir_label)

            # 4. Custom Container Widget: Speed Column (Styles fixed to match)
            speed_frame = QFrame()
            speed_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: #b0b0b0;
                    border-bottom: 1px solid #222222;
                }}
                QLabel {{
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }}
            """)
            speed_layout = QHBoxLayout(speed_frame)
            speed_layout.setContentsMargins(0, 0, 0, 0)
            speed_layout.setSpacing(0)
            
            speed_label = QLabel(speed_text)
            speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            speed_layout.addWidget(speed_label)

            # 5. Commit rows to their respective layout screens
            self.pressure_dir_list.addItem(dir_item)
            self.pressure_dir_list.setItemWidget(dir_item, dir_frame)

            self.pressure_speed_list.addItem(speed_item)
            self.pressure_speed_list.setItemWidget(speed_item, speed_frame)
    def open_log_viewer(self):
        try:
            # Unlock all log files
            for f in os.listdir(self.log_dir):
                if f.endswith(".awos"):
                    try:
                        unlock_file(os.path.join(self.log_dir, f))
                    except Exception as e:
                        print(f"Could not unlock {f}: {e}")

            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Log File",
                self.log_dir,
                "AWOS Files (*.awos);;All Files (*)"
            )

            if file_path:
                viewer = LogViewer(file_path, self)
                viewer.exec()      # Wait until LogViewer closes

        except Exception as e:
            print("Configuration Window Error:", e)

        finally:
            # Lock all log files again
            for f in os.listdir(self.log_dir):
                if f.endswith(".awos"):
                    try:
                        lock_file(os.path.join(self.log_dir, f))
                    except Exception as e:
                        print(f"Could not lock {f}: {e}")
            # logging.exception("Error to open View Log")
        
    # def open_log_viewer(self):
    #     try:
    #         logging.info("Opening View Log Window and Click On View Log Button")
    #         for f in os.listdir(self.log_dir):
    #             if f.endswith(".awos"):
    #                 unlock_file(os.path.join(self.log_dir, f))
    #         file_path, _ = QFileDialog.getOpenFileName(
    #             self, "Open Log File", self.log_dir,
    #             "AWOS Files (*.awos);;All Files (*)"   # ← changed
    #         )
    #         if file_path:
    #             viewer = LogViewer(file_path, self)
    #             viewer.exec()
    #     except Exception as e:
    #         print("Configuration Window Error:", e)
    #         logging.info("Error to open View Log")
    #         traceback.print_exc()

    def toggle_miu(self):
        if self.miu_label.isVisible():
            self.miu_label.hide()
        else:
            self.miu_label.show()
    
    def open_Config(self):
        try:
            if hasattr(self, "config_window") and self.config_window.isVisible():
                self.config_window.raise_()
                self.config_window.activateWindow()
                return

            self.config_window = ConfigurationWindow(
                parent=self,
                mode_label=self.mode_lbl
            )
            self.config_window.show()

        except Exception as e:
            print("Configuration Window Error:", e)
            traceback.print_exc()

 
    def Night_btn_Clicked(self):
    # Toggle mode logic
        self.is_night_mode = not self.is_night_mode

        # Standard Marine: Night = Red, Day = White
        if self.is_night_mode:

            color = "#e24707" 
            # self.rel_gauge = NeedleGauge(mode="RG")

            
            self.night_btn.setText("DAY")
        else:
            color = "white"
            self.night_btn.setText("NIGHT")

        # Common style for main value labels
        box_style = f"""
            QLabel {{
                color: {color};
                font-size: 50px;
              
                font-family: "Times New Roman";
                border: none;
                padding: 0px;
                line-height: 1;
            }}
        """

        # Common style for unit labels
        unit_style = f"""
            QLabel {{
                color: {color};
                font-size: 25px;
                font-weight:500;
                font-family: "Times New Roman";
                border: none;
                padding: 0px;
                margin: 0px;
                line-height: 1;
            }}
        """

        # Apply to all value boxes
        for box in [self.rel_box1,self.rel_box2,self.true_box1,self.true_box2 ]:
            box.setStyleSheet(box_style)
        # Apply to all units
        for unit in [self.rel_box1Unit,self.rel_box2Unit,self.true_box1Unit,self.true_box2Unit]:
            unit.setStyleSheet(unit_style)
        for lbl in [self.lat_lbl, self.long_lbl, self.time_lbl]:
            
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"""color: {color}; font-size: 29px; font-family: "Arial"; border: none;padding: 0px; margin: 0px;line-height: 1; """)

        for lbl in self.sensor_values.values():

            lbl.setStyleSheet(f"""border:none;color:{color};font-size:45px;font-family:Times New Roman;    
            """)
        self.mode_lbl.setStyleSheet(f"""color: {color}; font-size: 25px; font-weight: bold; font-family: "Arial"; border: none;""")

        self.sog_title.setStyleSheet(f"""color: {color};border: none;font-family: 'Times New Roman';font-size: 30px;font-weight: bold;""")
        self.cmg_title.setStyleSheet(f"""color: {color};border: none;font-family: 'Times New Roman';font-size: 30px;font-weight: bold;""")
        for hdr in self.sensor_headers.values():
            hdr.setStyleSheet(f"""border:none;color:{color};font-weight:bold;font-size:42px;font-family:Times New Roman;""")

        # Change unit color
        for unit in self.sensor_units.values():
            unit.setStyleSheet(f"""border:none;color:{color};font-weight:bold;font-size:28px;font-family:Times New Roman;
            """)

        self.rel_title.setText(f"""
        <span style='
        font-family:"Times New Roman";
        font-size:40px;
        font-weight:bold;
        color:{color};
        text-shadow:
        -1px -1px 0px #3498db,
        1px -1px 0px #3498db,
        -1px  1px 0px #3498db,
        1px  1px 0px #3498db,
        2px  2px 3px #000000;'>
        RELATIVE WIND
        </span>
        """)
        self.sog_bar.set_night_mode(self.is_night_mode)
        self.sog_bar.update()
        self.rel_gauge.set_night_mode(self.is_night_mode)
        self.rel_gauge.update()
        self.true_title.setText(f"""
        <span style='
        font-family:"Times New Roman";
        font-size:40px;
        font-weight:bold;
        color:{color};
        text-shadow:
        -1px -1px 0px #3498db,
        1px -1px 0px #3498db,
        -1px  1px 0px #3498db,
        1px  1px 0px #3498db,
        2px  2px 3px #000000;'>
        TRUE WIND
        </span>
        """)
        # for lbl in [self.deg_val_Unit,self.kts_val_Unit]:
        #     lbl.setStyleSheet(f""" color: {color}; font-size: 20px; font-weight: bold; font-family: "Times New Roman"; border: none;padding: 0px; margin: 0px;line-height: 1; """)
       
        for lbl in [self.deg_val,self.kts_val]:
            lbl.setStyleSheet(f"""color: {color};font-size: 38px;font-family: "Times New Roman";border: none;padding: 0px;margin: 0px; """)
      
        for lbl in [self.deg_val_unit,self.kts_val_unit]:
            lbl.setStyleSheet(f""" color: {color}; font-size: 20px; font-weight: bold; font-family: "Times New Roman"; border: none;padding: 0px; margin: 0px;line-height: 1; """)
       
        
   
    def create_sensor_tile(self, name, value, unit, sub_name="", sub_val="", sub_unit=""):
            tile = QFrame()
            tile.setFixedHeight(200)
            tile.setStyleSheet("""
                QFrame {
                    border: 2px solid #acacac;
                    background-color: black;
                }
            """)

            lay = QVBoxLayout(tile)
            lay.setContentsMargins(5, 10, 5, 5)
            lay.setSpacing(5)

            # TITLE (e.g., Relative Humidity, Temperature, Pressure, Visibility)
            name_lbl = QLabel(name)
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_lbl.setStyleSheet("""border:none;color:#fff;font-weight:bold;font-size:42px;font-family:Times New Roman;
            """)
            lay.addWidget(name_lbl)

            # VALUE CONTAINER ROW (Separates Number from Unit visual text)
            val_container = QHBoxLayout()
            val_container.setSpacing(5)
            val_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # MAIN VALUE NUMBER LABEL (CLICKABLE)
            val_lbl = ClickableLabel()
            val_lbl.setMinimumWidth(80)
            val_lbl.setText(str(value)) # Holds ONLY the raw number text
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            val_lbl.setStyleSheet("""
                border:none;
                color:white;
               
                font-size:45px;
                  font-family:Times New Roman;                       
            """)
            val_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            val_container.addWidget(val_lbl)

            # MAIN VALUE UNIT LABEL (STAYS PERSISTENT ON CLEAN CODES)
            unit_lbl = QLabel(unit) # Holds ONLY the standalone unit string
            unit_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
            unit_lbl.setStyleSheet("""
                border:none;
                color:white;
                font-weight:bold;
                font-size:28px;
                margin-bottom: 4px;  
                                    font-family:Times New Roman;    
            """)
            val_container.addWidget(unit_lbl)
            lay.addLayout(val_container)
            self.sensor_headers[name] = name_lbl
            self.sensor_units[name] = unit_lbl

            # CRITICAL MAP: Store ONLY the raw value label reference to your dictionary
            self.sensor_values[name] = val_lbl
            if name.lower() == "pressure":
                    self.pressure_dir_list = QListWidget(self)
                    self.pressure_speed_list = QListWidget(self)

                    for lst in [self.pressure_dir_list, self.pressure_speed_list]:
                        lst.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                        # Strip down the style sheet so it doesn't touch the items' background canvas
                            # Strip down the style sheet so it doesn't touch the items' background canvas
                        lst.setStyleSheet("""
                        
                            QListWidget {
                                background-color: #1a1a1a;
                                border: 4px solid #555555;
                                padding: 0px;
                                margin: 0px;
                                outline: none; /* Removes the hidden focus rectangle padding */
                            }
                            QListWidget::item {
                                padding: 0px;
                                margin: 0px;
                                background: transparent;
                            }
                            QListWidget::item:hover, QListWidget::item:selected {
                                background: transparent; /* Prevents blue/gray default hover selections */
                            }
                        """)
                        lst.setFixedWidth(60)  # Narrow width as seen in Image 1

                        lst.setVerticalScrollBarPolicy(
                            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
                        )
                        lst.setHorizontalScrollBarPolicy(
                            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
                        )
                        lst.setSizeAdjustPolicy(
                            QListWidget.SizeAdjustPolicy.AdjustToContents
                        )
                        lst.setFixedHeight(150)
                        lst.hide()     
                # Shared QSS Style Sheet for both spinboxes to create the clean layout with black arrows
                        spinbox_qss = """
                                        QSpinBox {
                            min-width: 25px;
                            max-width: 25px;
                            min-height: 40px;
                            background-color: white;
                            color: black;
                            border: 1px solid #555555;
                            border-radius: 2px;
                            /* Reduced vertical padding so text sits centrally between buttons */
                            padding: 20px 2px 20px 2px; 
                        }

                        QSpinBox::up-button {
                            subcontrol-origin: border;
                            subcontrol-position: top center; /* Aligns to the top */
                            width: 20px;
                            height: 20px;
                        }

                        QSpinBox::down-button {
                            subcontrol-origin: border;
                            subcontrol-position: bottom center; /* Aligns to the bottom */
                            width: 20px;
                            height: 20px;
                        }               
                                        """

                # Create the first spinbox (For Direction)
                        self.spinbox = QSpinBox(self)
                        self.spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
                        self.spinbox.setRange(0, 10)
                        self.spinbox.setValue(0)
                        self.spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.spinbox.setStyleSheet(spinbox_qss)

                        # Create the second spinbox (For Speed)
                        self.spinbox1 = QSpinBox(self)
                        self.spinbox1.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
                        self.spinbox1.setRange(0, 10)
                        self.spinbox1.setValue(0)
                        self.spinbox1.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.spinbox1.setStyleSheet(spinbox_qss)

                        # Layout coordinates
                        self.pressure_dir_list.move(-10, 10)
                        self.spinbox.move(170, 50)        # Aligned underneath the direction list

                        self.pressure_speed_list.move(315, 40)
                        self.spinbox1.move(280, 50)       # Aligned underneath the speed list
                        self.pressure_dir_list.raise_()
                        self.pressure_speed_list.raise_()

                        # Keeping them hidden initially as per your layout flow
                        self.spinbox.hide()
                        self.spinbox1.hide()
            # CLICK EVENT ASSIGNMENT
            val_lbl.clicked.connect(self.pressure_clicked)
         
            if sub_name:
                # SUB-TITLE LABEL (ALWAYS WHITE)
                sub_title_lbl = QLabel(sub_name)
                sub_title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                sub_title_lbl.setStyleSheet("""
                    border:none;
                    color:white;
                    font-weight:bold;
                    font-size:44px;
                                             font-family:Times New Roman;
                """)
                lay.addWidget(sub_title_lbl)

                # SUB-VALUE CONTAINER ROW
                sub_val_container = QHBoxLayout()
                sub_val_container.setSpacing(5)
                sub_val_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # SUB-VALUE NUMBER LABEL (NUMBER ONLY)
                sub_val_lbl = QLabel(str(sub_val))
                sub_val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                sub_val_lbl.setStyleSheet("""
                    border:none;
                    color:white;
                    
                    font-size:45px;
                                           font-family:Times New Roman;
                """)
                sub_val_container.addWidget(sub_val_lbl)

                # SUB-VALUE UNIT LABEL (SEPARATE AND PERSISTENT)
                sub_unit_lbl = QLabel(sub_unit if sub_unit else "°C")
                sub_unit_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
                sub_unit_lbl.setStyleSheet("""
                    border:none;
                    color:white;
                    font-weight:bold;
                    font-size:28px;
                    margin-bottom: 2px;
                                            font-family:Times New Roman;
                """)
                sub_val_container.addWidget(sub_unit_lbl)
                lay.addLayout(sub_val_container)
                self.sensor_headers[sub_name] = sub_title_lbl
                self.sensor_units[sub_name] = sub_unit_lbl

                self.sensor_values[sub_name] = sub_val_lbl

            return tile

    def closeEvent(self, event):
        finalize_log_file(self)
        ctypes.windll.user32.ShowWindow(ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None), 1)
        self.serial_thread.stop()
        self.serial_thread.wait()
        event.accept()

    