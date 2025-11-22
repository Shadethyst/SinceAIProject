import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSlot, QUrl, Qt
from PyQt6.QtCore import QStandardPaths
import re
import os
import winreg
import DragDropArea
import create_excel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selectedItem = ""
        self.start = True
        self.resize(800, 700)
        self.setWindowTitle("Since Hackathon Project")

        mainItems = QVBoxLayout()
        btnPdf = QPushButton(self)
        btnPdf.setFixedSize(120, 40)
        btnPdf.setText("Open File Dialog")
        btnPdf.clicked.connect(self.open_dialog)
        self.dragDialog = DragDropArea.DragDropArea()
        self.dragDialog.setMinimumHeight(150)

        mainItems.addWidget(btnPdf)
        mainItems.addWidget(self.dragDialog)
        mainItems.addStretch()

        self.dragDialog.onItemDropped.connect(self.pdfDropped)

        self.continue_button = QPushButton("Continue")
        self.continue_button.setFixedSize(120, 40)
        self.continue_button.setEnabled(False)
        self.continue_button.clicked.connect(self.show_completed_view)
        mainItems.addWidget(self.continue_button)

        itemWidget = QWidget()
        itemWidget.setLayout(mainItems)
        self.setCentralWidget(itemWidget)

    def show_completed_view(self):

        excel_button = QPushButton("Save Excel File")
        excel_button.setFixedSize(120, 40)

        row = QWidget()
        row_layout = QVBoxLayout()
        row_layout.setSpacing(20)

        label = QLabel("Calculation completed successfully. Click the button to save the Excel file.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row_layout.addWidget(label)

        row_layout.addWidget(excel_button, 0, Qt.AlignmentFlag.AlignHCenter)
        row.setLayout(row_layout)

        def on_create_clicked():
            filename, _ = QFileDialog.getSaveFileName(self, "Save Excel File", f"Laskentatiedosto", "Excel Files (*.xlsx)")
            if filename:
                create_excel.create_excel(name=filename)
                QApplication.instance().quit()

        excel_button.clicked.connect(on_create_clicked)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(row, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        container.setLayout(layout)

        self.setCentralWidget(container)
            
    @pyqtSlot()
    def open_dialog(self):
        #fname = QFileDialog.getOpenFileName(
        #    self,
        #    "Open File",
        #    "${HOME}",
        #    "PDF Files(*.pdf);; All Files(*)",
        #    )
        #reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        
        #downloads_path = winreg.QueryValueEx(reg_key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
        
        #winreg.CloseKey(reg_key)      
        workingdirectory = os.getcwd()
        fUrl = QFileDialog.getOpenFileUrl(
            self,
            "Select File",
            #QUrl(downloads_path),
            QUrl(workingdirectory),
            "PDF Files(*.pdf);; All Files(*)",
            )
#        print(fname)
        #print(downloads_path)
        print(fUrl[0].toString())
        
        if fUrl[0].toString().endswith(".pdf"):
            currentUrl = fUrl[0].toString()
            currentUrl = currentUrl[8:]
            self.selectedItem = currentUrl
            self.dragDialog.setText(currentUrl)
            try:
                self.continue_button.setEnabled(True)
            except Exception:
                pass
        else:
            self.dragDialog.setText("File not PDF")
            
    def pdfDropped(self):
        self.selectedItem = self.dragDialog.itemUrl[8:]
        print(self.selectedItem)
        try:
            self.continue_button.setEnabled(True)
        except Exception:
            pass
    pass

