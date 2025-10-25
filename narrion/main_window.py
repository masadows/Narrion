import os

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDockWidget,
    QLabel,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from tabs.battlemaps import build as build_battlemaps
from tabs.calendar import build as build_calendar
from tabs.dice.dice import build as build_dice
from tabs.initiative import build as build_initiative
from tabs.sessions import build as build_sessions
from themes import THEMES


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RPG Master Assistant")
        self.setWindowIcon(QIcon.fromTheme("applications-games"))

        central = QWidget()
        layout = QVBoxLayout(central)
        self.setCentralWidget(central)

        self.tabs = QTabWidget()
        self.tabs.addTab(build_sessions(), "Sesje RPG")
        self.tabs.addTab(build_battlemaps(), "Battlemapy")
        self.tabs.addTab(build_calendar(), "Terminarz sesji")

        layout.addWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Gotowe — UI mockup")

        self.current_theme = "Pydracula Dark"
        self.apply_theme(self.current_theme)

        self.dark_switch = QCheckBox()
        self.dark_switch.setChecked("Dark" in self.current_theme)
        self.dark_switch.stateChanged.connect(self.toggle_light_dark)

        tb = self._create_toolbar()
        self.addToolBar(tb)

        self.initiative_dock = None
        self.dice_dock = None

    def _create_toolbar(self) -> QToolBar:
        tb = QToolBar("Główne")
        tb.setIconSize(QSize(20, 20))

        act_initiative = QAction(QIcon.fromTheme("view-list-symbolic"), "Tracker inicjatywy", self)
        act_initiative.triggered.connect(self.open_initiative_dock)
        tb.addAction(act_initiative)

        icons_path = os.path.join(os.path.dirname(__file__), "icones")
        act_dice = QAction(QIcon(os.path.join(icons_path, "dice.png")), "Rzut kośćmi", self)
        act_dice.triggered.connect(self.open_dice_dock)
        tb.addAction(act_dice)

        tb.addWidget(QLabel("Motyw:"))
        self.theme_select = QComboBox()
        self.theme_select.addItems(THEMES.keys())
        self.theme_select.currentTextChanged.connect(self.apply_theme)
        tb.addWidget(self.theme_select)

        index = self.theme_select.findText(self.current_theme)
        if index != -1:
            self.theme_select.setCurrentIndex(index)

        self.theme_toggle = QCheckBox("", self)
        self.theme_toggle.stateChanged.connect(self.toggle_light_dark)

        tb.addWidget(self.theme_toggle)

        return tb

    def apply_theme(self, theme_name: str):
        path = THEMES.get(theme_name)
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    style = f.read()
                self.setStyleSheet(style)
                self.current_theme = theme_name
            except FileNotFoundError:
                print(f"Nie znaleziono pliku motywu: {path}")
        else:
            print(f"Nieznany motyw: {theme_name}")

    def toggle_light_dark(self, state):
        if not self.current_theme:
            return

        name_parts = self.current_theme.split()
        if "Dark" in name_parts:
            new_name = self.current_theme.replace("Dark", "Light")
        else:
            new_name = (
                self.current_theme.replace("Light", "Dark")
                if "Light" in name_parts
                else self.current_theme + " Dark"
            )

        if new_name in THEMES:
            self.theme_select.setCurrentText(new_name)

    def open_initiative_dock(self):
        if self.initiative_dock is None:
            self.initiative_dock = QDockWidget("Tracker inicjatywy", self)
            self.initiative_dock.setWidget(build_initiative())
            self.initiative_dock.setFeatures(
                QDockWidget.DockWidgetClosable
                | QDockWidget.DockWidgetMovable
                | QDockWidget.DockWidgetFloatable
            )
            self.addDockWidget(Qt.LeftDockWidgetArea, self.initiative_dock)
            self.initiative_dock.destroyed.connect(lambda: setattr(self, "initiative_dock", None))
        self.initiative_dock.show()
        self.initiative_dock.raise_()

    def open_dice_dock(self):
        if self.dice_dock is None:
            self.dice_dock = QDockWidget("Rzut kośćmi", self)
            self.dice_dock.setWidget(build_dice())
            self.dice_dock.setFeatures(
                QDockWidget.DockWidgetClosable
                | QDockWidget.DockWidgetMovable
                | QDockWidget.DockWidgetFloatable
            )
            self.addDockWidget(Qt.RightDockWidgetArea, self.dice_dock)
            self.dice_dock.setFixedSize(self.dice_dock.sizeHint())
            self.dice_dock.destroyed.connect(lambda: setattr(self, "dice_dock", None))
        self.dice_dock.show()
        self.dice_dock.raise_()
