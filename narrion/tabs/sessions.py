"""Campaign Session Management Module.

This module provides the top-level interface for managing RPG campaigns (sessions).
It functions as a navigation controller that switches between two main views:
1. **Session List (Dashboard):** A grid/list view of all available campaigns.
2. **Session Detail (Workspace):** A tabbed interface for a specific campaign,
   integrating Notes, Character sheets, and NPC databases.

The module handles the directory structure creation for new campaigns and
cleans up resources when campaigns are deleted.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from narrion.tabs.notes.notes import build as build_notes
from tabs.characters import CharacterType
from tabs.characters import build as build_characters


class SessionsTab(QWidget):
    """Main widget for campaign management.

    This widget manages the application state related to the active campaign.
    It does not use a `QStackedWidget` for navigation; instead, it dynamically
    rebuilds its own layout (`_clear_layout`) to switch between the selection
    screen and the campaign workspace.

    Attributes:
        SESSIONS_DIR (Path): Constant path to the root data directory ("data/sessions").
        sessions (list[str]): List of currently detected campaign directory names.
        current_session (str | None): Name of the currently active campaign, or None if in list view.
        layout (QVBoxLayout): The main layout container manipulated to change views.
    """

    SESSIONS_DIR = Path("data/sessions")

    def __init__(self):
        """Initialize the session manager and load existing campaigns."""
        super().__init__()

        self.sessions = []
        self._load_sessions()
        self.current_session = None

        self.layout = QVBoxLayout(self)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._build_session_list_ui()

    def _load_sessions(self):
        """Scan the data directory for existing campaign folders.

        Ensures the base directory exists and populates `self.sessions`
        with the names of subdirectories found.
        """
        self.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        self.sessions = [p.name for p in self.SESSIONS_DIR.iterdir() if p.is_dir()]

    def _build_session_list_ui(self):
        """Render the Dashboard view (List of Campaigns).

        Clears the current layout and builds the initial screen containing:
        - A list widget displaying available sessions.
        - Buttons to create a new campaign or delete an existing one.
        """
        self._clear_layout()
        self.current_session = None

        title = QLabel("<h2>Twoje kampanie RPG</h2>")
        title.setAlignment(Qt.AlignCenter)

        self.session_list = QListWidget()
        self.session_list.setViewMode(QListWidget.IconMode)
        self.session_list.setResizeMode(QListWidget.Adjust)
        self.session_list.setMovement(QListWidget.Static)
        self.session_list.setWrapping(True)
        self.session_list.setSpacing(12)
        # self.session_list.setWordWrap(True)
        # self.session_list.setUniformItemSizes(False)

        for s in self.sessions:
            self.session_list.addItem(s)
        self.session_list.itemDoubleClicked.connect(self.open_selected_session)

        btn_layout = QHBoxLayout()
        new_btn = QPushButton("Nowa kampania")
        new_btn.clicked.connect(self.add_session)
        delete_btn = QPushButton("Usuń kampanię")
        delete_btn.clicked.connect(self.delete_session)
        btn_layout.addWidget(new_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()

        self.layout.addWidget(title)
        self.layout.addWidget(self.session_list)
        self.layout.addLayout(btn_layout)

    def _build_session_detail_ui(self):
        """Render the Workspace view for the active campaign.

        Clears the dashboard layout and builds the tabbed interface containing:
        - Navigation button (Back to list).
        - Notes tab (loaded from `narrion.tabs.notes`).
        - Players tab (loaded from `tabs.characters`).
        - NPCs tab (loaded from `tabs.characters`).
        """
        self._clear_layout()

        back_btn = QPushButton("⬅ Wróć do listy kampanii")
        back_btn.clicked.connect(self._build_session_list_ui)

        label = QLabel(f"<h3>Kampania: {self.current_session}</h3>")
        label.setAlignment(Qt.AlignCenter)

        tabs = QTabWidget()
        tabs.addTab(build_notes(self.SESSIONS_DIR / self.current_session), "Notatki")
        tabs.addTab(build_characters(self.current_session, CharacterType.Player), "Gracze")
        tabs.addTab(build_characters(self.current_session, CharacterType.NPC), "Baza NPC")

        self.layout.addWidget(back_btn)
        self.layout.addWidget(label)
        self.layout.addWidget(tabs)

    def add_session(self):
        """Open a dialog to create a new campaign folder.

        If the name is valid and unique, creates the directory and updates the UI.
        """
        name, ok = QInputDialog.getText(self, "Nowa kampania", "Podaj nazwę kampanii:")
        if ok and name.strip():
            name = name.strip()
            if name not in self.sessions:
                self.sessions.append(name)
                if not self.current_session:
                    self.session_list.addItem(name)
                (self.SESSIONS_DIR / name).mkdir(parents=True, exist_ok=True)
            else:
                QMessageBox.warning(self, "Błąd", "Kampania o tej nazwie już istnieje.")

    def delete_session(self):
        """Delete the selected campaign and its data from the filesystem.

        Requires user confirmation via a QMessageBox. Uses `shutil.rmtree`
        to remove the campaign directory.
        """
        item = self.session_list.currentItem()
        if not item:
            QMessageBox.information(self, "Info", "Nie wybrano żadnej kampanii.")
            return

        name = item.text()
        confirm = QMessageBox.question(
            self,
            "Potwierdzenie",
            f"Czy na pewno chcesz usunąć kampanię '{name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.sessions.remove(name)
            session_path = self.SESSIONS_DIR / name
            import shutil

            shutil.rmtree(session_path)
            self._build_session_list_ui()

    def open_selected_session(self, item):
        """Transition from List View to Detail View for the clicked item.

        Args:
            item (QListWidgetItem): The session item clicked in the list.
        """
        name = item.text()
        self.current_session = name
        self._build_session_detail_ui()

    def _clear_layout(self):
        """Remove all widgets from the main layout.

        This acts as a 'screen wipe' to allow rebuilding the UI for a different view.
        """
        self._clear_layout_recursive(self.layout)

    def _clear_layout_recursive(self, layout):
        """Recursively delete all widgets and sub-layouts from a given layout.

        Args:
            layout (QLayout): The layout to clean.
        """
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self._clear_layout_recursive(item.layout())


def build() -> QWidget:
    """Factory function to create the SessionsTab widget.

    Returns:
        SessionsTab: The main session management widget.
    """
    return SessionsTab()
