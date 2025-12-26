from enum import Enum, auto
import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from widgets.section_header import SectionHeader

from .character import CharacterWidget


class CharacterType(Enum):
    Player = auto()
    NPC = auto()


class CharactersWidget(QWidget):
    CHARACTERS_DIR = Path("data/characters")

    def __init__(self, char_type: CharacterType = CharacterType.Player):
        super().__init__()
        self.char_type = char_type
        self.layout = QHBoxLayout(self)

        self.left = QVBoxLayout()

        header_text = "Gracze" if self.char_type == CharacterType.Player else "NPC"
        self.left.addWidget(SectionHeader(header_text))

        self.char_list = QListWidget()
        self.char_list.setObjectName("characterList")

        self.loaded_widgets = {}

        self.char_list.itemClicked.connect(self.open_selected_character)
        self.left.addWidget(self.char_list)

        buttons_layout = QHBoxLayout()

        self.add_char_button = QPushButton("Dodaj")
        self.add_char_button.clicked.connect(self.create_new_character)
        buttons_layout.addWidget(self.add_char_button)

        self.del_char_button = QPushButton("Usuń")
        self.del_char_button.clicked.connect(self.delete_character)
        buttons_layout.addWidget(self.del_char_button)

        self.left.addLayout(buttons_layout)

        self.left_container = QWidget()
        self.left_container.setLayout(self.left)
        self.left_container.setMaximumWidth(210)

        self.layout.addWidget(self.left_container)

        self.right_container = QWidget()
        self.clear_right_view()
        self.layout.addWidget(self.right_container, stretch=1)

        self.ensure_directories()
        self.load_characters()

        if self.char_list.count() > 0:
            self.char_list.setCurrentRow(0)
            self.open_selected_character(self.char_list.item(0))

    def ensure_directories(self):
        """Tworzy strukturę katalogów jeśli nie istnieje."""
        type_dir = self.CHARACTERS_DIR / self.char_type.name
        type_dir.mkdir(parents=True, exist_ok=True)

    def create_new_character(self):
        """Tworzy nową postać w UI oraz fizyczny plik JSON."""
        title = "Nowy Gracz" if self.char_type == CharacterType.Player else "Nowy NPC"
        name, ok = QInputDialog.getText(self, title, "Nazwa postaci:")

        if ok and name.strip():
            name = name.strip()

            if name in self.loaded_widgets:
                QMessageBox.warning(self, "Błąd", f"Postać o nazwie '{name}' już istnieje!")
                return

            type_dir = self.CHARACTERS_DIR / self.char_type.name
            file_path = type_dir / f"{name}.json"

            if file_path.exists():
                QMessageBox.warning(self, "Błąd", f"Plik dla postaci '{name}' już istnieje!")
                return

            default_data = {
                "name": name,
                "type": self.char_type.name,
                "short_description": "",
                "description": "",
                "stats_hp": "",
                "stats_ac": "",
                "stats_init": "",
                "image_path": None,
            }

            try:
                with file_path.open("w", encoding="utf-8") as f:
                    json.dump(default_data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                QMessageBox.critical(self, "Błąd zapisu", f"Nie udało się utworzyć pliku: {e}")
                return

            self.add_character_to_list(name)

            items = self.char_list.findItems(name, Qt.MatchExactly)
            if items:
                self.char_list.setCurrentItem(items[0])
                self.open_selected_character(items[0])

    def add_character_to_list(self, name: str):
        self.char_list.addItem(name)
        self.loaded_widgets[name] = CharacterWidget(name)

    def open_selected_character(self, item):
        if not item:
            return

        name = item.text()
        if name not in self.loaded_widgets:
            return

        target_widget = self.loaded_widgets[name]

        if self.right_container:
            self.layout.removeWidget(self.right_container)
            self.right_container.setParent(None)

        self.right_container = target_widget
        self.layout.addWidget(self.right_container, stretch=1)

    def load_characters(self):
        """Skanuje katalog i ładuje postać odpowiedniego typu."""
        type_dir = self.CHARACTERS_DIR / self.char_type.name

        if type_dir.exists():
            for item in sorted(type_dir.iterdir()):
                if item.is_file() and item.suffix == ".json":
                    self.add_character_to_list(item.stem)

    def delete_character(self):
        current_row = self.char_list.currentRow()
        current_item = self.char_list.currentItem()

        if current_row < 0 or not current_item:
            QMessageBox.information(self, "Info", "Wybierz postać do usunięcia.")
            return

        name = current_item.text()
        reply = QMessageBox.question(
            self,
            "Usuwanie postaci",
            f"Czy na pewno chcesz trwale usunąć postać: {name}?\nTego nie da się cofnąć.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        file_path = self.CHARACTERS_DIR / self.char_type.name / f"{name}.json"
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się usunąć pliku: {e}")
            return

        if name in self.loaded_widgets:
            del self.loaded_widgets[name]

        self.clear_right_view()

        self.char_list.takeItem(current_row)
        if self.char_list.count() > 0:
            new_row = min(current_row, self.char_list.count() - 1)
            self.char_list.setCurrentRow(new_row)
            self.open_selected_character(self.char_list.item(new_row))

    def clear_right_view(self):
        if self.right_container:
            self.layout.removeWidget(self.right_container)
            self.right_container.setParent(None)

        empty_widget = QLabel("Wybierz lub dodaj postać")
        empty_widget.setAlignment(Qt.AlignCenter)
        self.right_container = empty_widget
        self.layout.addWidget(self.right_container, stretch=1)


def build_players() -> QWidget:
    CharactersWidget.CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)
    return CharactersWidget(CharacterType.Player)


def build_npcs() -> QWidget:
    CharactersWidget.CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)
    return CharactersWidget(CharacterType.NPC)
