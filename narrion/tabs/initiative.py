import json
from pathlib import Path
from typing import List

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta

from themes import DEFAULT_FONT
from widgets.color_wrapper import color
from widgets.section_header import SectionHeader


class CharacterSelectionDialog(QDialog):
    """Dialog for selecting characters from the current campaign."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.campaign_path = None
        
        self.setWindowTitle("Wybierz postać")
        self.setModal(True)
        self.resize(400, 500)
        
        self.setup_ui()

    def fallback_setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Brak dostępnych kampanii. Najpierw utwórz kampanię."))
        buttons = QDialogButtonBox(
            QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)
        self.resize(300, 100)
    
    def setup_ui(self):

        campaign_layout = QHBoxLayout()
        campaign_layout.addWidget(QLabel("Kampania:"))
        
        campaigns_dir = Path("data/sessions")
        campaigns = [p.name for p in campaigns_dir.iterdir() if p.is_dir()] if campaigns_dir.exists() else []

        if not campaigns:
            self.fallback_setup_ui()
            return

        self.campaign_combo = QComboBox()
        self.campaign_combo.addItems(campaigns)
        self.campaign_combo.currentTextChanged.connect(self.on_campaign_changed)
        
        if campaigns:
            self.campaign_path = Path(f"data/sessions/{campaigns[0]}")
        
        campaign_layout.addWidget(self.campaign_combo)

        layout = QVBoxLayout(self)
        layout.addLayout(campaign_layout)
        
        # Character type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Typ postaci:"))
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Player", "NPC"])
        self.type_combo.currentTextChanged.connect(self.load_characters)
        type_layout.addWidget(self.type_combo)
        
        layout.addLayout(type_layout)
        
        # Character list
        layout.addWidget(QLabel("Wybierz postać:"))
        self.character_list = QListWidget()
        self.character_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.character_list)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.load_characters()

    def on_campaign_changed(self, campaign_name):
        """Handle campaign change."""
        self.campaign_path = Path(f"data/sessions/{campaign_name}")
        self.load_characters()
    
    def load_characters(self):
        """Load characters of the selected type."""
        if not self.campaign_path:
            return
        
        self.character_list.clear()
        
        char_type = self.type_combo.currentText()
        char_dir = self.campaign_path / "characters" / char_type
        
        if not char_dir.exists():
            return
        
        for char_file in sorted(char_dir.glob("*.json")):
            try:
                with open(char_file, 'r', encoding='utf-8') as f:
                    char_data = json.load(f)
                
                name = char_data.get('name', char_file.stem)
                description = char_data.get('short_description', '')
                
                display_text = name
                if description:
                    display_text += f"\n{description}"
                
                self.character_list.addItem(display_text)
                
            except (json.JSONDecodeError, IOError):
                # Skip invalid files
                continue
    
    def get_selected_character_data(self):
        """Get the selected character data."""
        current_item = self.character_list.currentItem()
        if not current_item:
            return None, None, None

        display_text = current_item.text()
        char_name = display_text.split("\n")[0]
        char_type = self.type_combo.currentText()
        
        char_file = self.campaign_path / "characters" / char_type / f"{char_name}.json"
        
        try:
            with open(char_file, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
            return char_name, char_type, char_data
        except (json.JSONDecodeError, IOError):
            return None, None, None


class InitiativeItemDelegate(QStyledItemDelegate):
    """Custom delegate for initiative table items."""

    def __init__(self, parent=None, min_value=1, max_value=30):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value

    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setRange(self.min_value, self.max_value)
        editor.setAlignment(Qt.AlignCenter)
        return editor

    def setEditorData(self, editor, index):
        value = int(index.model().data(index, Qt.EditRole))
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.value(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class StatusItemDelegate(QStyledItemDelegate):
    """Custom delegate for status table items."""

    def __init__(self, parent=None, statuses: List[str] = None):
        super().__init__(parent)
        self.statuses = statuses if statuses is not None else []

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.statuses)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        idx = editor.findText(value)
        if idx >= 0:
            editor.setCurrentIndex(idx)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


@color
class InitiativeTracker(QWidget):
    """Initiative tracker widget."""

    STATUSES = ["Żywy", "Ogłuszony", "Martwy"]
    INITIATIVE_RANGE = (0, 1000)
    BUTTONS_RESIZE_THRESHOLD = 450

    def __init__(self):
        super().__init__()
        self.current_turn = -1
        self.setup_ui()
        # remove after prototype
        self.load_sample_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        layout.addWidget(SectionHeader("Tracker inicjatywy"))

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Nazwa", "Inicjatywa", "Status"])

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.table.setItemDelegateForColumn(
            1, InitiativeItemDelegate(self.table, *self.INITIATIVE_RANGE)
        )
        self.table.setItemDelegateForColumn(2, StatusItemDelegate(self.table, self.STATUSES))

        layout.addWidget(self.table)

        controls = QHBoxLayout()
        self.add_btn = QPushButton("+")
        self.add_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_btn.clicked.connect(self.add_character)
        controls.addWidget(self.add_btn)

        self.remove_btn = QPushButton("−")
        self.remove_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.remove_btn.clicked.connect(self.remove_character)
        controls.addWidget(self.remove_btn)
        controls.addStretch()

        self.sort_btn = QPushButton("Sortuj")
        self.sort_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.sort_btn.clicked.connect(self.sort_by_initiative)
        controls.addWidget(self.sort_btn)

        self.next_btn = QPushButton()
        self.next_btn.setIcon(QIcon(qta.icon("mdi.skip-next", color=DEFAULT_FONT["icon_color"])))
        self.next_btn.icon_name = "mdi.skip-next"
        self.next_btn.setIconSize(QSize(20, 20))
        self.next_btn.setToolTip("Następna tura")
        self.next_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.next_btn.clicked.connect(self.next_turn)
        controls.addWidget(self.next_btn)

        layout.addLayout(controls)

    def load_sample_data(self):
        """Load sample data into the initiative tracker for testing. Only for prototype."""
        sample_characters = [
            ("Aldren", 18, "Żywy"),
            ("Szablozębny", 12, "Martwy"),
            ("Mag ciemności", 15, "Żywy"),
            ("Ork wojownik", 8, "Ogłuszony"),
            ("Elfka łuczniczka", 20, "Żywy"),
        ]

        for name, initiative, status in sample_characters:
            self.add_character_data(name, initiative, status)

    def add_character_data(self, name: str, initiative: int, status: str):
        """Add character data to the table."""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        name_item = QTableWidgetItem(name)
        self.table.setItem(row_position, 0, name_item)
        initiative_item = QTableWidgetItem(str(initiative))
        initiative_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row_position, 1, initiative_item)
        status_item = QTableWidgetItem(status)
        status_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row_position, 2, status_item)
        self.update_row_highlighting()

    def add_character(self):
        """Add a new character to the initiative tracker."""
        
        dialog = CharacterSelectionDialog(self)
        
        if dialog.exec() == QDialog.Accepted:
            char_name, char_type, char_data = dialog.get_selected_character_data()
            
            if not char_name or not char_data:
                QMessageBox.warning(self, "Błąd", "Nie udało się załadować danych postaci.")
                return
            
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0) and self.table.item(row, 0).text() == char_name:
                    QMessageBox.information(self, "Info", f"Postać {char_name} już jest w trackerze.")
                    return
            
            initiative_value = 10
            
            initiative, ok = QInputDialog.getInt(
                self,
                "Inicjatywa",
                f"Inicjatywa dla {char_name}:",
                value=initiative_value,
                minValue=self.INITIATIVE_RANGE[0],
                maxValue=self.INITIATIVE_RANGE[1],
            )
            
            if ok:
                self.add_character_data(char_name, initiative, self.STATUSES[0])

    def remove_character_data(self, row: int):
        """Remove character data from the table."""
        if 0 <= row < self.table.rowCount():
            self.table.removeRow(row)
            if self.current_turn >= self.table.rowCount():
                self.current_turn = self.table.rowCount() - 1
            self.update_row_highlighting()

    def remove_character(self):
        """Remove the selected character from the initiative tracker."""
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            name_item = self.table.item(selected_row, 0)
            name = name_item.text() if name_item else "Unknown"

            reply = QMessageBox.question(
                self,
                "Potwierdzenie usunięcia",
                f"Czy na pewno chcesz usunąć {name}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.remove_character_data(selected_row)
        else:
            QMessageBox.information(
                self, "Brak zaznaczenia", "Proszę zaznaczyć uczestnika do usunięcia."
            )

    def next_turn(self):
        """Advance to the next turn, skipping non-alive characters."""
        if self.table.rowCount() == 0:
            return

        attempts = 1

        while attempts < self.table.rowCount():
            self.current_turn = (self.current_turn + 1) % self.table.rowCount()
            status = self.get_character_status(self.current_turn)
            if status == self.STATUSES[0]:  # "Żywy"
                self.update_row_highlighting()
                return
            attempts += 1
        QMessageBox.information(
            self,
            "Brak żywych uczestników",
            "Wszyscy pozostali uczestnicy są martwi lub ogłuszeni.",
        )
        return

    def get_character_status(self, row: int) -> str:
        """Get the status of the character at the specified row."""
        if row < 0 or row >= self.table.rowCount():
            return self.STATUSES[2]  # "Martwy" - changed from [3] to [2]
        status_item = self.table.item(row, 2)
        return status_item.text() if status_item else self.STATUSES[0]

    def update_row_highlighting(self):
        """Update the highlighting of rows based on the current turn."""
        for row in range(self.table.rowCount()):
            if row == self.current_turn:
                self.highlight_row(row)
            else:
                self.dehighlight_row(row)

    def highlight_row(self, row: int):
        """Highlight the specified row."""
        if 0 <= row < self.table.rowCount():
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    font = item.font()
                    font.setUnderline(True)
                    font.setBold(True)
                    font.setItalic(True)
                    item.setFont(font)

    def dehighlight_row(self, row: int):
        """Remove highlighting from a row."""
        if 0 <= row < self.table.rowCount():
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    font = item.font()
                    font.setUnderline(False)
                    font.setBold(False)
                    font.setItalic(False)
                    item.setFont(font)

    def sort_by_initiative(self):
        """Sort characters by initiative (highest first), then by status (alive first)."""
        if self.table.rowCount() == 0:
            return

        characters = []
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            name = name_item.text() if name_item else ""

            initiative_widget = self.table.item(row, 1)
            initiative = (
                int(initiative_widget.text()) if initiative_widget else self.INITIATIVE_RANGE[0]
            )

            status_widget = self.table.item(row, 2)
            status = status_widget.text() if status_widget else self.STATUSES[0]

            characters.append((name, initiative, status))

        status_priority = {}
        for status in self.STATUSES:
            status_priority[status] = self.STATUSES.index(status)
        characters.sort(key=lambda x: (-x[1], status_priority.get(x[2], 0)))

        self.table.setRowCount(0)
        self.current_turn = 0

        for name, initiative, status in characters:
            self.add_character_data(name, initiative, status)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.table.width() < self.BUTTONS_RESIZE_THRESHOLD:
            self.add_btn.setText("")
            self.add_btn.setIcon(qta.icon("ei.plus", color=DEFAULT_FONT["icon_color"]))
            self.add_btn.icon_name = "ei.plus"
            self.remove_btn.setText("")
            self.remove_btn.setIcon(qta.icon("ei.minus", color=DEFAULT_FONT["icon_color"]))
            self.remove_btn.icon_name = "ei.minus"
            self.sort_btn.setText("")
            self.sort_btn.setIcon(qta.icon("fa5s.sort", color=DEFAULT_FONT["icon_color"]))
            self.sort_btn.icon_name = "fa5s.sort"
        else:
            self.add_btn.setIcon(QIcon())
            self.add_btn.setText("Dodaj uczestnika")
            self.remove_btn.setIcon(QIcon())
            self.remove_btn.setText("Usuń uczestnika")
            self.sort_btn.setIcon(QIcon())
            self.sort_btn.setText("Sortuj według inicjatywy")

    def changeFontColor(self, icon_color):
        if self.table.width() < self.BUTTONS_RESIZE_THRESHOLD:
            for btn in [self.next_btn, self.add_btn, self.remove_btn, self.sort_btn]:
                btn.setIcon(qta.icon(btn.icon_name, color=icon_color))


def build() -> InitiativeTracker:
    """Build and return the initiative tracker widget."""
    return InitiativeTracker()
