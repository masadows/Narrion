from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from widgets.section_header import SectionHeader

from .character import CharacterWidget
from enum import Enum, auto
from pathlib import Path
import json


class CharacterType(Enum):
    Player = auto()
    NPC = auto()


class CharactersWidget(QWidget):
    CARACTERS_DIR = Path("data/characters")

    def __init__(self, type: CharacterType = CharacterType.Player):
        super().__init__()
        self.layout = QHBoxLayout(self)

        self.left = QVBoxLayout()
        if type == CharacterType.Player:
            self.left.addWidget(SectionHeader("Gracze"))
        else:
            self.left.addWidget(SectionHeader("NPC"))

        self.char_list = QListWidget()
        self.char_list.setObjectName("characterList")
        self.player_list = {}

        for p in ["Aldren (Gracz)", "Mira (Gracz)", "Szablozębny (NPC)"]:
            self.char_list.addItem(p)
            self.player_list[p] = CharacterWidget(p)
        self.load_characters(CharacterType.Player)

        self.char_list.itemClicked.connect(self.open_selected_character)
        self.left.addWidget(self.char_list)

        self.add_player_button = QPushButton("Dodaj postać")
        self.add_player_button.clicked.connect(self.create_new_character)
        self.left.addWidget(self.add_player_button)

        self.left_container = QWidget()
        self.left_container.setLayout(self.left)
        self.left_container.setMaximumWidth(210)

        self.layout.addWidget(self.left_container)

        if self.player_list:
            first_player_widget = list(self.player_list.values())[0]
            self.char_list.setCurrentRow(0)
        else:
            first_player_widget = QWidget()
        self.right_container = first_player_widget
        self.layout.addWidget(self.right_container, stretch=1)

    def create_new_character(self):
        name, ok = QInputDialog.getText(self, "Nowa postać", "Nazwa postaci")
        if ok and name.strip():
            name = name.strip()
            if name in self.player_list:
                QMessageBox.warning(self, "Błąd", f"Postać o nazwie '{name}' już istnieje!")
                return
            self.char_list.addItem(name)
            self.player_list[name] = CharacterWidget(name)

    def open_selected_character(self, item):
        name = item.text()
        player_widget = self.player_list[name]

        self.layout.removeWidget(self.right_container)
        self.right_container.setParent(None)

        self.right_container = player_widget
        self.layout.addWidget(self.right_container, stretch=1)

    def load_characters(self, type: CharacterType):
        type_dir = CharactersWidget.CARACTERS_DIR / type.name
        type_dir.mkdir(parents=True, exist_ok=True)
        if type == CharacterType.Player:
            for item in type_dir.iterdir():
                if item.is_file() and item.suffix == ".json":
                    with item.open("r", encoding="utf-8") as f:
                        data = json.load(f)
                    self.char_list.addItem(item.stem)
                    self.player_list[item.stem] = CharacterWidget(item.stem)

        else:
            pass


def build() -> QWidget:
    CharactersWidget.CARACTERS_DIR.mkdir(parents=True, exist_ok=True)
    return CharactersWidget()
