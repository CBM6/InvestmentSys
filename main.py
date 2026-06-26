import sys
import PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout, QLabel

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Investment Assistant")
window.resize(900, 600)

