import sys
import os
import shutil
import tempfile
from pathlib import Path
import PySide6


# Tell Qt where PySide6 installed its platform plugins.
# This prevents macOS/PyCharm from starting Qt with an empty plugin path.
qt_plugins_path = Path(PySide6.__file__).resolve().parent / "Qt" / "plugins"
qt_platforms_path = qt_plugins_path / "platforms"

# PyCharm can mark files inside an excluded virtual environment as hidden.
# Qt ignores hidden platform plugins, so copy only those plugins to a visible
# temporary directory instead of repeatedly modifying the virtual environment.
visible_platform_plugins = tempfile.TemporaryDirectory(
    prefix="investmentsys-qt-platforms-"
)
visible_platforms_path = Path(visible_platform_plugins.name)

for plugin_path in qt_platforms_path.iterdir():
    if plugin_path.is_file():
        shutil.copyfile(plugin_path, visible_platforms_path / plugin_path.name)

os.environ["QT_PLUGIN_PATH"] = str(qt_plugins_path)
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(visible_platforms_path)

from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow


#Create Qt application obj
app = QApplication(sys.argv)
#Create and show the main window
window = MainWindow()
window.show()
#Start the app event loop
sys.exit(app.exec())
