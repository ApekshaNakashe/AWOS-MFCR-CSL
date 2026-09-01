from ui.common import *
import traceback

class MaintenanceDialog(QDialog):
    def __init__(self, raw_sentence, parent=None):
        super().__init__(parent)
# cs
        try:
            self.setWindowTitle("Maintenance")
            self.setFixedSize(750, 160)
            self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
            self.setStyleSheet("""
                QDialog {
                    background-color: #d4d4d4;
                }
            """)
    

            layout = QVBoxLayout(self)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(4)

            
            # mfcr_lbl = QLabel("MFCR")
            # mfcr_lbl.setStyleSheet("""
            #     background:transparent;
            #     color:black;
            #     font-weight:bold;
            #     border:none;
            #     padding-left:2px;
            # """)
            # layout.addWidget(mfcr_lbl)

            # --------------------------------------------------
            # Parse Sentence
            # --------------------------------------------------
            raw = str(raw_sentence).strip()

            chk = ""
            if "*" in raw:
                raw_without_chk, chk = raw.rsplit("*", 1)
                chk = chk.strip()
            else:
                raw_without_chk = raw

            parts = raw_without_chk.split(",")

            labels = {
                0: "Header,",
                1: "WSP,",
                4: "WSS,",
                7: "Gyro,",
                8: "Log,",
                9: "HM,",
                10: "TEMP,",
                11: "DEW,",
                12: "PRES,",
                13: "TIME,",
                14: "LAT,",
                16: "LONG,",
                18: "SOG,",
                19: "COG,",
                20: "DATE,",
                21: "Visibility,",
                22: "Ver,"
            }

            # --------------------------------------------------
            # Calculate field positions
            # --------------------------------------------------
            field_start = []
            pos = 0

            for part in parts:
                field_start.append(pos)
                pos += len(part) + 1

            total_len = max(len(raw), pos + 100)

            header_chars = [" "] * total_len

            for field_idx, label in labels.items():

                if field_idx >= len(field_start):
                    continue

                start = field_start[field_idx]
                if field_idx == 22:  # 'Ver,' field
                    if 21 in labels and 21 < len(field_start):
                        vis_start = field_start[21]
                        vis_len = len(labels[21])
                        # If 'Ver' starts before 'Visibility' ends, push it right
                        if start < (vis_start + vis_len):
                            start = vis_start + vis_len
                for i, ch in enumerate(label):

                    idx = start + i

                    if idx < len(header_chars):
                        header_chars[idx] = ch

            header_line = "".join(header_chars).rstrip()

            # --------------------------------------------------
            # Shared container
            # --------------------------------------------------
            container = QWidget()
            container_layout = QVBoxLayout(container)

            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(0)

            font = QFont("Courier New", 8)
            font.setStyleHint(QFont.StyleHint.TypeWriter)

            # --------------------------------------------------
            # White sentence box
            # --------------------------------------------------
            self.display = QTextEdit()
            self.display.setFixedWidth(850)
            self.display.setReadOnly(True)

            self.display.setLineWrapMode(
                QTextEdit.LineWrapMode.NoWrap
            )

            self.display.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

            self.display.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

            self.display.setFixedHeight(35)

            self.display.setFont(font)

            self.display.setStyleSheet("""
                QTextEdit {
                    background:white;
                    color:black;
                    border:1px solid black;
                    padding:2px;
                }
            """)

            self.display.setPlainText(raw)

            # --------------------------------------------------
            # Header outside box
            # --------------------------------------------------
            headers_lbl = QLabel(header_line)

            headers_lbl.setFont(font)

            headers_lbl.setStyleSheet("""
                QLabel {
                    border:none;
                    background:#d4d4d4;
                    color:black;
                    padding-left:4px;
                }
            """)

            container_layout.addWidget(self.display)
            container_layout.addWidget(headers_lbl)

            # --------------------------------------------------
            # Scroll Area
            # --------------------------------------------------
            scroll = QScrollArea()

            scroll.setWidget(container)
            scroll.setWidgetResizable(False)

            scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOn
            )

            scroll.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

            scroll.setStyleSheet("""
                QScrollArea {
                    border:none;
                    background:#d4d4d4;
                }
            """)

            fm = QFontMetrics(font)

            required_width = max(
                fm.horizontalAdvance(raw),
                fm.horizontalAdvance(header_line)
            ) + 30

            container.setMinimumWidth(required_width)

            layout.addWidget(scroll)

            # --------------------------------------------------
            # Exit Button
            # --------------------------------------------------
            self.exit_btn = QPushButton("EXIT")

            self.exit_btn.setFixedSize(120, 40)

            self.exit_btn.setStyleSheet("""
                QPushButton {
                    background:#c0c0c0;
                    border:2px solid black;
                    font-weight:bold;
                    color:black;
                }
            """)

            self.exit_btn.clicked.connect(self.accept)

            layout.addWidget(
                self.exit_btn,
                alignment=Qt.AlignmentFlag.AlignCenter
            )

        except Exception as e:
            print(f"Maintenance Dialog Error: {e}")
            traceback.print_exc()

            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open Maintenance Dialog.\n\n{e}"
            )
    def update_sentence(self, sentence):
            self.display.setText(sentence)