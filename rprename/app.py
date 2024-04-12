import sys

from PyQt6.QtWidgets import QApplication

from .views import Window


def main():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())