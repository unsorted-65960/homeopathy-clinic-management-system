# main.py
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from database import models as dbmodels
from database.database import init_db_if_exists
from controllers.main_controller import MainController


def main():
    # Initialize database (only if exists — won’t create a new one)
    db_present = init_db_if_exists(dbmodels.Base)

    # Create application
    app = QApplication(sys.argv)

    # --- ACTUAL working scroll-prevention ---
    from PySide6.QtWidgets import (
        QSpinBox,
        QDoubleSpinBox,
        QComboBox,
        QDateEdit,
        QDateTimeEdit,
        QTimeEdit,
    )

    # helper function to patch a class's wheelEvent
    def disable_scroll(cls):
        def wheelEvent(self, event):
            if self.hasFocus():
                super(cls, self).wheelEvent(event)
            else:
                event.ignore()
        cls.wheelEvent = wheelEvent

    for widget_cls in (QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit, QDateTimeEdit, QTimeEdit):
        disable_scroll(widget_cls)

    # --- Load global QSS stylesheet ---
    style_path = Path(__file__).resolve().parent / "assets" / "style.qss"
    if style_path.exists():
        try:
            with open(style_path, "r", encoding="utf-8") as f:
                qss = f.read()
                app.setStyleSheet(qss)
                print(f"✅ Loaded QSS theme: {style_path.name}")
        except Exception as e:
            print(f"⚠️ Failed to load QSS: {e}")
    else:
        print("⚠️ No QSS found — running with default Qt style")

    # --- Main window setup ---
    win = QMainWindow()
    win.setWindowTitle("Homeopathy Clinic — Demo")
    win.setMinimumSize(900, 600)

    stack = QStackedWidget()
    win.setCentralWidget(stack)

    # Controller manages navigation
    ctrl = MainController(stack, base=dbmodels.Base)

    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
