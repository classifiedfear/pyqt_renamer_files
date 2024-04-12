import sys
import typing
from PyQt6 import QtCore

from PyQt6.QtWidgets import (
    QApplication,
    QDialog, 
    QMainWindow,
    QMessageBox,
    QWidget
)

from PyQt6.uic import load_ui

from main_window_ui import Ui_MainWindow
class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None ) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.actionExit.triggered.connect(self.close)
        self.actionFind_and_Replace.triggered.connect(self.findAndReplace)
        
    def findAndReplace(self):
        dialog = FindReplaceDialog(self)
        dialog.exec()


class FindReplaceDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        load_ui.loadUi('find_replace.ui', self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec())