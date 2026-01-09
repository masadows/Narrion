#!/usr/bin/env python3
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLibraryInfo

from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    translator = QTranslator()
    translator.load("qtbase_pl", QLibraryInfo.path(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)
    win = MainWindow()
    win.show()
    win.showNormal()
    sys.exit(app.exec())
