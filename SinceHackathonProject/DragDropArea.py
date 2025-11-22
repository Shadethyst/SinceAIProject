from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import pyqtSignal
import sys

class DragDropArea(QLineEdit):
    onItemDropped = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.itemUrl = ""
        

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        eventText = event.mimeData().text()
        print(eventText)
        if eventText.endswith(".pdf"):
            self.setText(eventText)
            self.itemUrl = eventText
        else:
            self.setText("File not PDF")
            self.itemUrl = ""
        print(self.itemUrl)
        self.onItemDropped.emit(self.itemUrl)

    pass




