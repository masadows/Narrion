"""Main Application Window and Navigation Controller.

This module defines the entry point for the graphical user interface.
"""

import json
import os
from pathlib import Path
import shutil

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta

from narrion.tabs.battlemaps.battlemaps import build as build_battlemaps
from tabs.calendar import build as build_calendar
from tabs.dice.dice import build as build_dice
from tabs.initiative import build as build_initiative
from tabs.sessions import build as build_sessions
from themes import DEFAULT_FONT, THEMES
from widgets.color_wrapper import COLOR_LISTENERS


class MainWindow(QMainWindow):
    """The root window of the RPG Master Assistant application.

    This class serves as the central hub for the application. It implements
    a responsive layout that adapts the sidebar based on window width and
    manages the state of active themes.



    Attributes:
        central (QWidget): The central container widget.
        side_panel (QWidget): The collapsible navigation sidebar.
        stack (QStackedWidget): The container for main pages (Sessions, Battlemaps, etc.).
        page_buttons (list[QPushButton]): References to navigation buttons for state updates.
        current_theme (str): The name of the currently active QSS theme.
        initiative_dock (QDockWidget | None): Handle for the Initiative Tracker dock.
        dice_dock (QDockWidget | None): Handle for the Dice Roller dock.
    """

    def __init__(self):
        """Initialize the main window, UI components, and theme engine."""
        super().__init__()
        self.load_settings()
        self.setWindowTitle("RPG Master Assistant")
        self.setWindowIcon(QIcon.fromTheme("applications-games"))

        self.central = QWidget()
        main_layout = QHBoxLayout(self.central)
        self.setCentralWidget(self.central)

        self.side_panel = QWidget()
        side_layout = QVBoxLayout(self.side_panel)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(0)

        self.buttons_info = [
            ("Kampanie RPG", "fa5s.book-open", 0),
            ("Battlemapy", "fa5s.map", 1),
            ("Terminarz", "fa5s.calendar-alt", 2),
            ("Kości", "fa5s.dice-d20", "dice"),
            ("Tracker", "fa5s.list-ol", "tracker"),
        ]

        self.page_buttons = []
        for text, icon, idx in self.buttons_info:
            btn = QPushButton(qta.icon(icon, color=DEFAULT_FONT["icon_color"]), text)
            btn.icon_name = icon
            btn.setIconSize(QSize(24, 24))
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setObjectName("menuButtons")
            btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))
            side_layout.addWidget(btn)
            self.page_buttons.append(btn)

        side_layout.addStretch()

        self.side_panel.setFixedWidth(160)
        main_layout.addWidget(self.side_panel)

        self.stack = QStackedWidget()
        self.pages = [
            build_sessions(),
            build_battlemaps(),
            QWidget(),
        ]
        for page in self.pages:
            self.stack.addWidget(page)

        main_layout.addWidget(self.stack)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Gotowe — UI mockup")

        self.current_theme = self.settings.get("theme")
        self.apply_theme(self.current_theme)

        self.dark_switch = QCheckBox()
        self.dark_switch.setChecked("Dark" in self.current_theme)
        self.dark_switch.stateChanged.connect(self.toggle_light_dark)

        tb = self._create_toolbar()
        self.addToolBar(tb)

        self.initiative_dock = None
        self.dice_dock = None

        self.switch_page(0)

    def load_settings(self):
        settings_path = Path("./data/settings.json")
        basic_path = Path("./data/default_settings.json")
        if not settings_path.exists():
            shutil.copy(basic_path, settings_path)

        with open(settings_path, "r") as file:
            self.settings = json.load(file)

    def save_settings(self):
        with open("./data/settings.json", "w") as file:
            json.dump(self.settings, file, indent=4)

    def _create_toolbar(self) -> QToolBar:
        """Construct the top toolbar with theme controls.

        Returns:
            QToolBar: The configured toolbar widget.
        """
        tb = QToolBar("Główne")
        tb.setIconSize(QSize(20, 20))

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
        """Apply a new visual theme to the application.

        Args:
            theme_name (str): The key name of the theme in `THEMES`.
        """
        theme_info = THEMES.get(theme_name)
        if theme_info:
            try:
                path = theme_info["path"]
                icon_color = theme_info["icon_color"]
                DEFAULT_FONT["name"] = theme_name
                DEFAULT_FONT["icon_color"] = icon_color
                with open(path, "r", encoding="utf-8") as f:
                    style = f.read()
                self.setStyleSheet(style)
                self.current_theme = theme_name

                for btn in self.page_buttons:
                    btn.setIcon(qta.icon(btn.icon_name, color=icon_color))

                for cls in COLOR_LISTENERS:
                    cls.changeFontColor(icon_color)
                self.settings["theme"] = theme_name
                self.save_settings()
            except FileNotFoundError:
                print(f"Nie znaleziono pliku motywu: {path}")
        else:
            print(f"Nieznany motyw: {theme_name}")

    def toggle_light_dark(self, state):
        """Switch between Light and Dark variants of the current theme.

        Assumes theme naming convention like "Name Light" and "Name Dark".

        Args:
            state (int): Checkbox state (unused, logic relies on current name).
        """
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

    def switch_page(self, index: int | str):
        """Navigate to a specific page or toggle a dock widget.

        Handles routing logic:
        - **Int**: Switch the `QStackedWidget` to the given index.
        - **"dice" / "tracker"**: Open/Show the corresponding `QDockWidget`.
        - **Calendar (index 2)**: Checks for credentials before lazy loading.

        Args:
            index (int | str): The target destination identifier.
        """
        for btn in self.page_buttons:
            btn.setChecked(False)

        if index == "dice":
            self.open_dice_dock()
            self.page_buttons[3].setChecked(True)
            return
        elif index == "tracker":
            self.open_initiative_dock()
            self.page_buttons[4].setChecked(True)
            return

        if index == 2:
            if not os.path.exists("./data/credentials.json"):
                self._show_calendar_credentials_missing()
                return

            if not hasattr(self, "_calendar_loaded"):
                calendar_page = build_calendar()
                self.stack.removeWidget(self.stack.widget(2))
                self.stack.insertWidget(2, calendar_page)
                self._calendar_loaded = True

        if isinstance(index, int):
            self.stack.setCurrentIndex(index)
            self.page_buttons[index].setChecked(True)

    def _show_calendar_credentials_missing(self):
        """Display an alert dialog if Google Calendar credentials are missing."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Brak konfiguracji kalendarza")
        msg.setText(
            "Nie znaleziono pliku credentials.json.\n"
            "Aby korzystać z kalendarza, skonfiguruj integrację i "
            "umieść plik w:\n./data/credentials.json\n"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def resizeEvent(self, event):
        """Handle window resize to provide responsive UI.

        Collapses the sidebar to icons-only mode when width < 900px.

        Args:
            event (QResizeEvent): The resize event.
        """
        super().resizeEvent(event)
        if self.central.width() < 900:
            for btn in self.page_buttons:
                btn.setText("")
            self.side_panel.setFixedWidth(50)
        else:
            for (text, _, _), btn in zip(self.buttons_info, self.page_buttons):
                btn.setText(text)
            self.side_panel.setFixedWidth(160)

    def open_initiative_dock(self):
        """Create or show the Initiative Tracker dock widget."""
        if self.initiative_dock is None:
            self.initiative_dock = QDockWidget("Tracker inicjatywy", self)
            self.initiative_dock.setWidget(build_initiative())
            self.initiative_dock.setFeatures(
                QDockWidget.DockWidgetClosable
                | QDockWidget.DockWidgetMovable
                | QDockWidget.DockWidgetFloatable
            )
            self.addDockWidget(Qt.RightDockWidgetArea, self.initiative_dock)
            self.initiative_dock.destroyed.connect(lambda: setattr(self, "initiative_dock", None))
        self.initiative_dock.show()

    def open_dice_dock(self):
        """Create or show the Dice Roller dock widget."""
        if self.dice_dock is None:
            self.dice_dock = QDockWidget("Rzut kośćmi", self)
            self.dice_dock.setWidget(build_dice())
            self.dice_dock.setFeatures(
                QDockWidget.DockWidgetClosable
                | QDockWidget.DockWidgetMovable
                | QDockWidget.DockWidgetFloatable
            )
            self.addDockWidget(Qt.RightDockWidgetArea, self.dice_dock)
            self.dice_dock.setFixedWidth(self.dice_dock.sizeHint().width())
            self.dice_dock.destroyed.connect(lambda: setattr(self, "dice_dock", None))
        self.dice_dock.show()
