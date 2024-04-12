from collections import deque
from pathlib import Path

from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QWidget, QFileDialog

from .ui.window import Ui_Window

from .rename import Renamer

FILTERS = ";;".join(
    (
    "PNG Files (*.png)",
    "JPEG Files (*.jpeg)",
    "JPG Files (*.jpg)",
    'GIF Files (*.gif)',
    'Text Files (*.txt)',
    "Python Files (*.py)"
    )
)

class Window(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._files = deque()
        self._filesCount = len(self._files)
        self.ui = Ui_Window()
        self._setupUI()
        self._connectSignalsSlots()


    def _setupUI(self):
        self.ui.setupUi(self)
        self._updateStateWhenNoFiles()

    def _updateStateWhenNoFiles(self):
        self._filesCount = len(self._files)
        self.ui.loadFilesButton.setEnabled(True)
        self.ui.loadFilesButton.setFocus()
        self.ui.renameFilesButton.setEnabled(False)
        self.ui.prefixEdit.clear()
        self.ui.prefixEdit.setEnabled(False)


    def _connectSignalsSlots(self):
        self.ui.loadFilesButton.clicked.connect(self.loadFiles)
        self.ui.renameFilesButton.clicked.connect(self.renameFiles)
        self.ui.prefixEdit.textChanged.connect(self._updateStateWhenReady)

    def _updateStateWhenReady(self):
        if self.ui.prefixEdit.text():
            self.ui.renameFilesButton.setEnabled(True)
        else: 
            self.ui.renameFilesButton.setEnabled(False)
    
    def loadFiles(self):
        self.ui.dstFiIeList.clear()
        if self.ui.dirEdit.text():
            initDir = self.ui.dirEdit.text()
        else:
            initDir = str(Path.home())
        files, filter = QFileDialog.getOpenFileNames(
            self, 'Choose Files to Rename', initDir, filter=FILTERS
        )
        if len(files) > 0:
            fileExtension = filter[filter.index('*') : -1]
            self.ui.extensionLabel.setText(fileExtension)
            srcDirName = str(Path(files[0]).parent)
            self.ui.dirEdit.setText(srcDirName)
            for file in files:
                self._files.append(Path(file))
                self.ui.srcFileList.addItem(file)
            self._filesCount = len(self._files)
            self._updateStateWhenFilesLoaded()

    def _updateStateWhenFilesLoaded(self):
        self.ui.prefixEdit.setEnabled(True)
        self.ui.prefixEdit.setFocus()

    def renameFiles(self):
        self._runRenamerThread()
        self._updateStateWhileRenaming()

    def _updateStateWhileRenaming(self):
        self.ui.loadFilesButton.setEnabled(False)
        self.ui.renameFilesButton.setEnabled(False)

    
    def _runRenamerThread(self):
        prefix = self.ui.prefixEdit.text()
        self._thread = QThread()
        self._renamer = Renamer(
            files=tuple(self._files),
            prefix=prefix
        )
        self._renamer.moveToThread(self._thread)
        self._thread.started.connect(self._renamer.renameFiles)
        self._renamer.renamedFile.connect(self._updateStateWhenFileRenamed)
        self._renamer.progressed.connect(self._updateProgressBar)
        self._renamer.finished.connect(self._updateStateWhenNoFiles)
        self._renamer.finished.connect(self._thread.quit)
        self._renamer.finished.connect(self._renamer.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()


    def _updateStateWhenFileRenamed(self, newFile):
        self._files.popleft()
        self.ui.srcFileList.takeItem(0)
        self.ui.dstFiIeList.addItem(str(newFile))

    def _updateProgressBar(self, fileNumber):
        progressPercent = int(fileNumber / self._filesCount * 100)
        self.ui.progressBar.setValue(progressPercent)