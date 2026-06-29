import sys
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow



#Create Qt application obj
app = QApplication(sys.argv)
#Create and show the main window
window = MainWindow()
window.show()
#Start the app event loop
sys.exit(app.exec())


