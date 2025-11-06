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

from .player import CharacterWidget


class CharactersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)

        self.left = QVBoxLayout()
        self.left.addWidget(SectionHeader("Gracze"))

        self.char_list = QListWidget()
        self.char_list.setObjectName("characterList")
        self.player_list = {}

        for p in ["Aldren (Gracz)", "Mira (Gracz)", "Szablozębny (NPC)"]:
            self.char_list.addItem(p)
            self.player_list[p] = CharacterWidget(p)

        self.char_list.itemClicked.connect(self.open_selected_player)
        self.left.addWidget(self.char_list)

        self.add_player_button = QPushButton("Dodaj gracza")
        self.add_player_button.clicked.connect(self.create_new_player)
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

    def create_new_player(self):
        name, ok = QInputDialog.getText(self, "Nowy gracz", "Nazwa postaci")
        if ok and name.strip():
            name = name.strip()
            if name in self.player_list:
                QMessageBox.warning(self, "Błąd", f"Gracz o nazwie '{name}' już istnieje!")
                return
            self.char_list.addItem(name)
            self.player_list[name] = CharacterWidget(name)

    def open_selected_player(self, item):
        name = item.text()
        player_widget = self.player_list[name]

        self.layout.removeWidget(self.right_container)
        self.right_container.setParent(None)

        self.right_container = player_widget
        self.layout.addWidget(self.right_container, stretch=1)


def build() -> QWidget:
    return CharactersWidget()
