import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QFileDialog, QVBoxLayout
from PyQt6.QtCore import pyqtSlot, QUrl
from PyQt6.QtCore import QStandardPaths
import re
import os
import winreg
import DragDropArea

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selectedItem = ""
        mainItems = QVBoxLayout()
        btnPdf = QPushButton(self)
        btnPdf.setText("Open File Dialog")
        btnPdf.clicked.connect(self.open_dialog)
        self.dragDialog = DragDropArea.DragDropArea()

        mainItems.addWidget(btnPdf)
        mainItems.addWidget(self.dragDialog)
        self.dragDialog.onItemDropped.connect(self.pdfDropped)
        itemWidget = QWidget()
        itemWidget.setLayout(mainItems)
        
        self.setCentralWidget(itemWidget)
    @pyqtSlot()
    def open_dialog(self):
        #fname = QFileDialog.getOpenFileName(
        #    self,
        #    "Open File",
        #    "${HOME}",
        #    "PDF Files(*.pdf);; All Files(*)",
        #    )
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        
        downloads_path = winreg.QueryValueEx(reg_key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
        
        winreg.CloseKey(reg_key)      
        fUrl = QFileDialog.getOpenFileUrl(
            self,
            "Open File",
            QUrl(downloads_path),
            "PDF Files(*.pdf);; All Files(*)",
            )
#        print(fname)
        print(downloads_path)
        print(fUrl[0].toString())
        
        if fUrl[0].toString().endswith(".pdf"):
            self.selectedItem = fUrl[0].toString()
            self.dragDialog.setText(fUrl[0].toString())
        else:
            self.dragDialog.setText("File not PDF")
            
    def pdfDropped(self):
        self.selectedItem = self.dragDialog.itemUrl
        print(self.selectedItem)
    pass




