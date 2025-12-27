# tabs/sessions.py
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
    SESSIONS_DIR = Path("data/sessions")

    def __init__(self):
        super().__init__()

        self.sessions = []
        self._load_sessions()
        self.current_session = None

        self.layout = QVBoxLayout(self)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._build_session_list_ui()

    def _load_sessions(self):
        """Loads the list of existing sessions from the data/sessions directory"""
        self.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        self.sessions = [p.name for p in self.SESSIONS_DIR.iterdir() if p.is_dir()]

    def _build_session_list_ui(self):
        """Ekran startowy z listą sesji"""
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
        new_btn = QPushButton("➕ Nowa kampania")
        new_btn.clicked.connect(self.add_session)
        delete_btn = QPushButton("🗑️ Usuń kampanię")
        delete_btn.clicked.connect(self.delete_session)
        btn_layout.addWidget(new_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()

        self.layout.addWidget(title)
        self.layout.addWidget(self.session_list)
        self.layout.addLayout(btn_layout)

    def _build_session_detail_ui(self):
        """Ekran sesji z zakładkami"""
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
        name = item.text()
        self.current_session = name
        self._build_session_detail_ui()

    def _clear_layout(self):
        """Czyści cały layout (używane przy przełączaniu widoków)"""
        self._clear_layout_recursive(self.layout)

    def _clear_layout_recursive(self, layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self._clear_layout_recursive(item.layout())


def build():
    return SessionsTab()
