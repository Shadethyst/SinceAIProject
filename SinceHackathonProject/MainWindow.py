import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSlot, QUrl, Qt, QTimer, pyqtSignal
from PyQt6.QtCore import QStandardPaths
import re
import os
import winreg
import DragDropArea
import create_excel
from eisko_crop import eisko_crop

class MainWindow(QMainWindow):
    def __init__(self):
         
        super().__init__()
        self.selectedItem = ""
        self.resize(600, 300)
        self.setWindowTitle("Since Hackathon Project")

        self.onContinue = pyqtSignal(str)
        mainItems = QVBoxLayout()

        top_text_default = "Drag and drop a PDF file or use the button to select one."
        self.top_label = QLabel(top_text_default)
        self.top_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.top_label.setFixedHeight(40)
        mainItems.addWidget(self.top_label)

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
        self.startWidget = itemWidget

    @pyqtSlot()
    def show_completed_view(self):
        processor = eisko_crop()
        processor.callOnContinue(self.selectedItem)
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
                create_excel(name=filename)
                QTimer.singleShot(100, self.reset_to_start)

        excel_button.clicked.connect(on_create_clicked)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(row, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        container.setLayout(layout)

        try: 
            old = self.takeCentralWidget()
            if old is not None:
                self.startWidget = old
        except Exception:
            pass

        self.setCentralWidget(container)
            
    @pyqtSlot()
    def open_dialog(self):
        workingdirectory = os.getcwd()
        fUrl = QFileDialog.getOpenFileUrl(
            self,
            "Select File",
            QUrl(workingdirectory),
            "PDF Files(*.pdf);; All Files(*)",
            )
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

    def reset_to_start(self):

        self.selectedItem = ""
        self.top_label.setText("Excel file created successfully.")
        
        try:
            self.dragDialog.setText("")
            self.continue_button.setEnabled(False)
            self.setCentralWidget(self.startWidget)

        except Exception as e:
            print(e)
            pass