from ui.common import *
import traceback
def update_all_blinking(self):
    try:
        for key, blinking in self.blink_flags.items():

            label = self.blink_labels[key]

            if blinking:

                # toggle visibility effect using stylesheet
                current = label.styleSheet()

                if "yellow" in current:
                    label.setStyleSheet("""
                        color: transparent;
                        background-color: transparent;
                        border: none;
                    """)
                else:
                    label.setStyleSheet("""
                        background-color: yellow;
                        color: red;
                        font-weight: bold;
                        font-size: 12px;
                        border: 1px solid black;
                        padding: 5px;
                        qproperty-alignment: AlignCenter;
                        height:10px;
                        margin:10px 0px 10px 0px;
                    """)

    except Exception as e:
        print(f"update_all_blinking Error: {e}")
        traceback.print_exc()


def handle_status_label(self, key, raw_value):

    try:
        value = str(raw_value).strip().upper() if raw_value is not None else ""

        label = self.blink_labels[key]

        # ---- DEFAULT HIDDEN LOOK (space remains fixed)
        if value == "" or value not in ["INF", "+INF", "-INF"]:

            self.blink_flags[key] = False

            label.setStyleSheet("""
                color: transparent;
                background-color: transparent;
                border: none;
            """)

            return

        # ---- INF → ENABLE BLINK
        if value in ["INF", "+INF", "-INF"]:
            self.blink_flags[key] = True

    except Exception as e:
        print(f"handle_status_label Error: {e}")
        traceback.print_exc()