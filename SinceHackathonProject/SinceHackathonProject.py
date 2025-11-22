from PyQt6.QtWidgets import QApplication
import sys
import MainWindow

app = QApplication(sys.argv)
main_qui = MainWindow.MainWindow()
main_qui.show()
sys.exit(app.exec())


