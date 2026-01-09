"""Application Entry Point.

This module serves as the main launcher for the RPG Master Assistant application.
It initializes the core Qt framework, instantiates the main application window,
and begins the graphical event loop.

Usage:
    Run this script directly from the terminal to start the application:
    $ make run
"""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLibraryInfo

from main_window import MainWindow

if __name__ == "__main__":
    """Main execution block.
    
    Initializes the QApplication with command line arguments.
    """
    app = QApplication(sys.argv)
    translator = QTranslator()
    translator.load("qtbase_pl", QLibraryInfo.path(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)
    win = MainWindow()
    win.show()
    win.showNormal()
    sys.exit(app.exec())
