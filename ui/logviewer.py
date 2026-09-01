from ui.common import *
from cryptography.fernet import Fernet
from ui.accessfile import unlock_file,lock_file
KEY = b"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx="
cipher = Fernet(KEY)
LOG_FORMAT = (
    "20s20s20s"
    "20s20s20s20s20s20s20s20s20s20s20s20s"
    "20s20s20s20s20s20s20s20s20s20s"
    "2i"
)


RECORD_SIZE = struct.calcsize(LOG_FORMAT)
class BinaryMmapModel(QAbstractTableModel):

    def __init__(self, columns, parent=None):
        super().__init__(parent)

        self.columns = columns
        self.mm = None
        self.row_count = 0

    def set_mmap(self, mm):

        self.mm = mm

        # self.row_count = len(mm) // RECORD_SIZE
        self.offsets = []

        offset = 0

        while offset < len(mm):

            self.offsets.append(offset)

            enc_size = struct.unpack(
                "I",
                mm[offset:offset+4]
            )[0]

            offset += 4 + enc_size
        self.row_count = len(self.offsets)

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return len(self.columns)

    def headerData(self, section, orientation, role):

        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.columns[section]

        return str(section + 1)
    def data(self, index, role):

        if role != Qt.DisplayRole:
            return None

        row = index.row()
        col = index.column()

        try:
            offset = self.offsets[row]

            enc_size = struct.unpack(
                "I",
                self.mm[offset:offset + 4]
            )[0]

            offset += 4

            encrypted = self.mm[offset:offset + enc_size]

            decrypted = cipher.decrypt(encrypted)

            record = struct.unpack(
                LOG_FORMAT,
                decrypted
            )

            if col < 25:
                return record[col].decode(
                    "utf-8",
                    errors="ignore"
                ).rstrip("\0")

            return str(record[col])

        except Exception:
            # logger.exception(f"Error reading row={row}, col={col}")
            return ""
    # def data(self, index, role):

    #     if role != Qt.DisplayRole:
    #         return None

    #     row = index.row()
    #     col = index.column()

    #     offset = row * RECORD_SIZE

    #     raw = self.mm[offset:offset + RECORD_SIZE]

    #     if len(raw) != RECORD_SIZE:
    #         return ""

    #     try:
    #         record = struct.unpack(LOG_FORMAT,raw)

    #     except:
    #         return ""
    #     if col in range(25):   # Columns 0 to 24
    #         return record[col].decode(
    #             "utf-8",
    #             errors="ignore"
    #         ).rstrip("\0")
    #     else:                  # Columns 25 and 26
    #         return str(record[col])
    
class NoCopyTableView(QTableView):
    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            event.ignore()
            return
        super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        event.ignore()

class LogViewer(QDialog):
    def __init__(self, log_file, parent=None):
        super().__init__(parent)
        self.log_file = log_file
        # logger.info("log window is opening")
        self.setWindowTitle("Log Viewer.vi rev. 12")
        self.resize(1000, 600)
        self.setStyleSheet("background-color: #f0f0f0; color: black;")

        self.cols = [
            "SYS Date", "SYS Time", "GPS Time", "WSP_Dir", "WSP_spd",
            "WSS_Dir", "WSS_spd", "Rel Wind Dir", "Rel Wind Speed",
            "True Wind Dir", "True Wind Speed", "COG", "SOG", "LOG", "GYRO",
            "MODE", "sensor_selection", "sensor_selected", "latitude", "longitude",
            "Humidity", "Dew Point","Tempture","Pressure","Visiblity" ,"Avg", "Stray Limit"
        ]

        layout = QVBoxLayout(self)

        self.view = NoCopyTableView()
        self.model = BinaryMmapModel(self.cols)
        self.view.setModel(self.model)

        self.view.setEditTriggers(QTableView.NoEditTriggers)
        self.view.setSelectionMode(QAbstractItemView.NoSelection)
        
        header = self.view.horizontalHeader()
        fm = self.view.fontMetrics()
        for col, text in enumerate(self.cols):
            width = fm.horizontalAdvance(text) + 60
            self.view.setColumnWidth(col, width)
        self.view.setColumnWidth(15, 150)
        self.view.setColumnWidth(18, 150)   # lat
        self.view.setColumnWidth(19, 150)
       
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.verticalHeader().setDefaultSectionSize(22)
        layout.addWidget(self.view)

        status_layout = QHBoxLayout()
        self.status_label = QLabel("Opening...")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        btn_layout = QHBoxLayout()
        self.cpyStatement=QLabel()
        self.cpyStatement.setText("press COPY to get data in EXCEL form for evalution of data")
        self.export_btn = QPushButton("COPY")
        exit_btn = QPushButton("EXIT")
        for btn in [self.export_btn, exit_btn]:
            btn.setFixedSize(120, 35)
            btn.setStyleSheet("background-color: #c0c0c0; border: 2px solid gray;")
        exit_btn.clicked.connect(self.close)
        self.export_btn.clicked.connect(self._save_as_csv)
        btn_layout.addStretch()
        btn_layout.addWidget(self.cpyStatement)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(exit_btn)
        layout.addLayout(btn_layout)

        self._mmap_file = None
        self._mm = None
        self.indexer = None
        self.open_file()
    def open_file(self):
        try:
            if not os.path.exists(self.log_file):
                self.status_label.setText("File not found")
                # logger.info("File Not Found")
                return

            if os.path.getsize(self.log_file) == 0:
                self.status_label.setText("File is empty")
                # logger.info("File is Found")
                return

            # Give access
            unlock_file(self.log_file)
            # logger.info("File is unlocked after unlock function")
            self._mmap_file = open(self.log_file, "rb")
            # logger.info("File opened successfully")
            self._mm = mmap.mmap(
                self._mmap_file.fileno(),
                0,
                access=mmap.ACCESS_READ
            )
            # logger.info("Memory Map Created")

            self.model.set_mmap(self._mm)
            # logger.info("Model loaded")
            self.status_label.setText(
                f"Loaded {self.model.rowCount():,} rows"
            )

        except Exception as e:
           
            # logger.exception("Exception in open_file()")
            QMessageBox.critical(self, "Error", traceback.format_exc())
            # QMessageBox.critical(self, "Error", str(e))

    # def open_file(self):
    #     try:
    #         if not os.path.exists(self.log_file):
    #             self.status_label.setText("File not found")
    #             return
    #         file_size = os.path.getsize(self.log_file)
    #         if file_size == 0:
    #             self.status_label.setText("File is empty")
    #             return
    #         unlock_file(self.log_file)
    #         self._mmap_file = open(self.log_file,"rb")

    #         self._mm = mmap.mmap(self._mmap_file.fileno(),0,access=mmap.ACCESS_READ)

    #         self.model.set_mmap(self._mm)

    #         self.status_label.setText( f"")

    #     except Exception as e:

    #         QMessageBox.critical(
    #             self,
    #             "Error",
    #             str(e)
    #         )
   
    def _on_index_finished(self):
        self.status_label.setText(f"Loaded {self.model.rowCount():,} rows")

    # def _save_as_csv(self):
    #     default_name = os.path.splitext(self.log_file)[0] + ".csv"

    #     file_path, _ = QFileDialog.getSaveFileName(self,"Export CSV",default_name,"CSV Files (*.csv)")
    #     if not file_path:
    #         return
    #     try:
    #         with open(file_path, "w", newline="", encoding="utf-8") as f:
    #             writer = csv.writer(f)
    #             writer.writerow(self.cols)
    #             # rows = len(self._mm) // RECORD_SIZE
    #             # for row in range(rows):
    #                 # offset = row * RECORD_SIZE
    #                 # raw = self._mm[offset: offset + RECORD_SIZE]
    #                 # if len(raw) != RECORD_SIZE:
    #                 #     continue
    #                 # record = struct.unpack(LOG_FORMAT, raw)
    #             offset = 0

    #             while offset < len(self._mm):

    #                     enc_size = struct.unpack(
    #                         "I",
    #                         self._mm[offset:offset+4]
    #                     )[0]

    #                     offset += 4

    #                     encrypted = self._mm[offset:offset+enc_size]

    #                     offset += enc_size

    #                     decrypted = cipher.decrypt(encrypted)

    #                     record = struct.unpack(
    #                         LOG_FORMAT,
    #                         decrypted
    #                     )
    #                 out = []   
    #                 for i, value in enumerate(record):

    #                     if i < 25:          # first 25 fields are strings
    #                         out.append(
    #                             value.decode(
    #                                 "utf-8",
    #                                 errors="ignore"
    #                             ).rstrip("\0")
    #                         )
    #                     else:               # last 2 fields are integers
    #                         out.append(value)

    #                 writer.writerow(out)
    #         QMessageBox.information(
    #             self,
    #             "Success",
    #             f"CSV saved:\n{file_path}"
    #         )

    #     except Exception as e:

    #         QMessageBox.critical(
    #             self,
    #             "Export Error",
    #             str(e)
    #         )
    def _save_as_csv(self):

        default_name = os.path.splitext(self.log_file)[0] + ".csv"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV",
            default_name,
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:

            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:

                writer = csv.writer(f)
                writer.writerow(self.cols)

                offset = 0

                while offset < len(self._mm):

                    # Read encrypted record size
                    enc_size = struct.unpack(
                        "I",
                        self._mm[offset:offset + 4]
                    )[0]

                    offset += 4

                    # Read encrypted data
                    encrypted = self._mm[offset:offset + enc_size]

                    offset += enc_size

                    # Decrypt
                    decrypted = cipher.decrypt(encrypted)

                    # Unpack
                    record = struct.unpack(
                        LOG_FORMAT,
                        decrypted
                    )

                    out = []

                    for i, value in enumerate(record):

                        if i < 25:
                            out.append(
                                value.decode(
                                    "utf-8",
                                    errors="ignore"
                                ).rstrip("\0")
                            )
                        else:
                            out.append(str(value))

                    writer.writerow(out)

            QMessageBox.information(
                self,
                "Success",
                f"CSV saved:\n{file_path}"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Export Error",
                str(e)
            )
    def _export_done(self, path):
        self.export_btn.setEnabled(True)
        self.export_btn.setText("EXPORT CSV")
        QMessageBox.information(self, "Success", f"Saved to:\n{path}")

    def _export_error(self, message):
        self.export_btn.setEnabled(True)
        self.export_btn.setText("EXPORT CSV")
        QMessageBox.critical(self, "Export Error", message)
    def closeEvent(self, event):

        try:
            
            if self.indexer and self.indexer.isRunning():
                self.indexer.stop()
                self.indexer.wait()

            if self._mm:
                self._mm.close()
                self._mm = None

            if self._mmap_file:
                self._mmap_file.close()
                self._mmap_file = None

            # Lock AFTER closing
            lock_file(self.log_file)

        except Exception as e:
            print(e)

        super().closeEvent(event)
   
   
   
    # def closeEvent(self, event):
    #     if self.indexer and self.indexer.isRunning():
    #         self.indexer.stop()
    #         self.indexer.wait()
    #     if self._mm:
    #         self._mm.close()
    #     if self._mmap_file:
    #         self._mmap_file.close()
    #     lock_file(self.log_file)
    #     super().closeEvent(event)
