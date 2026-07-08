import sys
import os
import subprocess
from pathlib import Path
import PySide6


# Tell Qt where PySide6 installed its platform plugins.
# This prevents macOS/PyCharm from starting Qt with an empty plugin path.
qt_plugins_path = Path(PySide6.__file__).resolve().parent / "Qt" / "plugins"
qt_platforms_path = qt_plugins_path / "platforms"
os.environ.setdefault("QT_PLUGIN_PATH", str(qt_plugins_path))
os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", str(qt_platforms_path))

# macOS sometimes marks PySide6 plugin files as hidden after environment rebuilds.
# Qt then scans the folder but fails to recognize the cocoa platform plugin.
subprocess.run(["chflags", "-R", "nohidden", str(qt_plugins_path)], check=False)

from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow


#Create Qt application obj
app = QApplication(sys.argv)
#Create and show the main window
window = MainWindow()
window.show()
#Start the app event loop
sys.exit(app.exec())
