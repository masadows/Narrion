"""Initiative tracking system for tabletop RPG sessions.

This module provides a complete initiative tracker interface including:
- Character selection from campaigns
- Initiative order management
- Character status tracking (Alive, Stunned, Dead)
- Turn progression with automatic skipping of non-alive characters

The module consists of several components:
- CharacterSelectionDialog: Dialog for selecting characters from campaigns
- InitiativeItemDelegate: Custom editor for initiative values
- StatusItemDelegate: Custom editor for character status
- InitiativeTracker: Main widget for managing initiative order
"""

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
    """Dialog for selecting characters from available campaigns.

    This dialog allows users to:
    - Select from available campaigns
    - Choose between Player and NPC character types
    - Browse and select specific characters from the chosen campaign and type

    Attributes:
        campaign_path (Path): Path to the currently selected campaign directory
        campaign_combo (QComboBox): Dropdown for campaign selection
        type_combo (QComboBox): Dropdown for character type selection
        character_list (QListWidget): List of available characters
    """

    def __init__(self, parent=None):
        """Initialize the character selection dialog.

        Args:
            parent: Parent widget, defaults to None
        """
        super().__init__(parent)
        self.campaign_path = None

        self.setWindowTitle("Wybierz postać")
        self.setModal(True)
        self.resize(400, 500)

        self.setup_ui()

    def fallback_setup_ui(self):
        """Set up fallback UI when no campaigns are available.

        Creates a simple dialog with a message about no available campaigns
        and a Cancel button.
        """
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Brak dostępnych kampanii. Najpierw utwórz kampanię."))
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel, Qt.Horizontal)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)
        self.resize(300, 100)

    def setup_ui(self):
        """Set up the main UI components.

        Creates the dialog layout with:
        - Campaign selection dropdown
        - Character type selection (Player/NPC) dropdown
        - Character list display
        - OK/Cancel buttons

        Falls back to simple UI if no campaigns are found.
        """
        campaign_layout = QHBoxLayout()
        campaign_layout.addWidget(QLabel("Kampania:"))

        campaigns_dir = Path("data/sessions")
        campaigns = (
            [p.name for p in campaigns_dir.iterdir() if p.is_dir()]
            if campaigns_dir.exists()
            else []
        )

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
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.load_characters()

    def on_campaign_changed(self, campaign_name: str):
        """Handle campaign selection change.

        Updates the campaign path and reloads the character list
        for the newly selected campaign.

        Args:
            campaign_name (str): Name of the selected campaign
        """
        self.campaign_path = Path(f"data/sessions/{campaign_name}")
        self.load_characters()

    def load_characters(self):
        """Load characters of the currently selected campaign and type.

        Reads character JSON files from the campaign/type directory and populates
        the character list. Character display includes name and short description
        if available. Invalid JSON files are skipped silently.
        """
        if not self.campaign_path:
            return

        self.character_list.clear()

        char_type = self.type_combo.currentText()
        char_dir = self.campaign_path / "characters" / char_type

        if not char_dir.exists():
            return

        for char_file in sorted(char_dir.glob("*.json")):
            try:
                with open(char_file, "r", encoding="utf-8") as f:
                    char_data = json.load(f)

                name = char_data.get("name", char_file.stem)
                description = char_data.get("short_description", "")

                display_text = name
                if description:
                    display_text += f"\n{description}"

                self.character_list.addItem(display_text)

            except (json.JSONDecodeError, IOError):
                # Skip invalid files
                continue

    def get_selected_character_data(self) -> tuple[str, str]:
        """Get the selected character's name and type.

        Returns:
            str: Tuple of (character name, character type) or None if no selection

        """
        current_item = self.character_list.currentItem()
        if not current_item:
            return None

        display_text = current_item.text()
        char_name = display_text.split("\n")[0]
        char_type = self.type_combo.currentText()
        return char_name, char_type


class InitiativeItemDelegate(QStyledItemDelegate):
    """Custom delegate for editing initiative values in the table.

    Provides a QSpinBox editor with configurable min/max values
    for editing initiative scores in the initiative tracker table.

    Attributes:
        min_value (int): Minimum allowed initiative value
        max_value (int): Maximum allowed initiative value
    """

    def __init__(self, parent=None, min_value=1, max_value=30):
        """Initialize the initiative item delegate.

        Args:
            parent: Parent widget, defaults to None
            min_value (int): Minimum initiative value, defaults to 1
            max_value (int): Maximum initiative value, defaults to 30
        """
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value

    def createEditor(self, parent, option, index) -> QSpinBox:
        """Create a QSpinBox editor for initiative values.

        Args:
            parent: Parent widget for the editor
            option: Style option information
            index: Model index being edited

        Returns:
            QSpinBox: Configured spin box editor
        """
        editor = QSpinBox(parent)
        editor.setRange(self.min_value, self.max_value)
        editor.setAlignment(Qt.AlignCenter)
        return editor

    def setEditorData(self, editor: QSpinBox, index):
        """Sets the data to be displayed and edited by the editor from the data model item specified by the model index.

        Args:
            editor: The QSpinBox editor
            index: Model index containing the data
        """
        value = int(index.model().data(index, Qt.EditRole))
        editor.setValue(value)

    def setModelData(self, editor: QSpinBox, model, index):
        """Gets data from the editor widget and stores it in the specified model at the item index.

        Args:
            editor: The QSpinBox editor
            model: The table model
            index: Model index to update
        """
        model.setData(index, editor.value(), Qt.EditRole)

    def updateEditorGeometry(self, editor: QSpinBox, option, index):
        """Updates the editor for the item specified by index according to the style option given.

        Args:
            editor: The QSpinBox editor
            option: Style option containing geometry information
            index: Model index being edited
        """
        editor.setGeometry(option.rect)


class StatusItemDelegate(QStyledItemDelegate):
    """Custom delegate for editing character status in the table.

    Provides a QComboBox editor with predefined status options
    for editing character status values in the initiative tracker.

    Attributes:
        statuses (List[str]): List of available status options
    """

    def __init__(self, parent=None, statuses: List[str] = None):
        """Initialize the status item delegate.

        Args:
            parent: Parent widget, defaults to None
            statuses (List[str]): List of available status options, defaults to empty list
        """
        super().__init__(parent)
        self.statuses = statuses if statuses is not None else []

    def createEditor(self, parent, option, index) -> QComboBox:
        """Create a QComboBox editor for status values.

        Args:
            parent: Parent widget for the editor
            option: Style option information
            index: Model index being edited

        Returns:
            QComboBox: Configured combo box editor with status options
        """
        editor = QComboBox(parent)
        editor.addItems(self.statuses)
        return editor

    def setEditorData(self, editor: QComboBox, index):
        """Sets the data to be displayed and edited by the editor from the data model item specified by the model index.

        Args:
            editor: The QComboBox editor
            index: Model index containing the data
        """
        value = index.model().data(index, Qt.EditRole)
        idx = editor.findText(value)
        if idx >= 0:
            editor.setCurrentIndex(idx)

    def setModelData(self, editor: QComboBox, model, index):
        """Gets data from the editor widget and stores it in the specified model at the item index.

        Args:
            editor: The QComboBox editor
            model: The table model
            index: Model index to update
        """
        model.setData(index, editor.currentText(), Qt.EditRole)

    def updateEditorGeometry(self, editor: QComboBox, option, index):
        """Updates the editor for the item specified by index according to the style option given.

        Args:
            editor: The QComboBox editor
            option: Style option containing geometry information
            index: Model index being edited
        """
        editor.setGeometry(option.rect)


@color
class InitiativeTracker(QWidget):
    """Main initiative tracking widget for tabletop RPG sessions.

    This widget provides a complete initiative management system including:
    - Adding characters defined in campaigns
    - Initiative order tracking
    - Turn progression with status awareness
    - Character status management (Alive, Stunned, Dead)
    - Responsive UI that adapts to different screen sizes

    Class Attributes:
        STATUSES (List[str]): Available character status options
        INITIATIVE_RANGE (tuple): Min and max values for initiative scores
        BUTTONS_RESIZE_THRESHOLD (int): Width threshold for using image-only buttons

    Attributes:
        current_turn (int): Index of the character whose turn it currently is
        table (QTableWidget): Main table displaying characters and their data
        add_btn (QPushButton): Button to add new characters
        remove_btn (QPushButton): Button to remove selected characters
        sort_btn (QPushButton): Button to sort characters by initiative
        next_btn (QPushButton): Button to advance to next character's turn
    """

    STATUSES = ["Żywy", "Ogłuszony", "Martwy"]
    INITIATIVE_RANGE = (0, 1000)
    BUTTONS_RESIZE_THRESHOLD = 450

    def __init__(self):
        """Initialize the initiative tracker widget.

        Sets up the UI components.
        """
        super().__init__()
        self.current_turn = -1
        self.setup_ui()

    def setup_ui(self):
        """Set up the main UI components.

        Creates the layout with:
        - Section header
        - Initiative table with custom delegates
        - Control buttons (add, remove, sort, next turn)
        - Responsive button behavior
        """
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

    def add_character_data(self, name: str, initiative: int, status: str):
        """Add a character to the initiative table.

        Creates a new table row with the character's information and
        updates the row highlighting to reflect the current turn.

        Args:
            name (str): Character's name
            initiative (int): Character's initiative value
            status (str): Character's current status
        """
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
        """Add a new character through the character selection dialog.

        Opens the character selection dialog, allows the user to choose
        a character of a selected type from available campaigns, prompts for initiative value,
        and adds the character to the tracker. Prevents duplicate entries..
        """

        dialog = CharacterSelectionDialog(self)

        if dialog.exec() == QDialog.Accepted:
            char_name, char_type = dialog.get_selected_character_data()

            if not char_name or not char_type:
                QMessageBox.warning(self, "Błąd", "Nie udało się załadować danych postaci.")
                return

            char_table_name = f"{char_name} ({char_type})"

            for row in range(self.table.rowCount()):
                if self.table.item(row, 0) and self.table.item(row, 0).text() == char_table_name:
                    QMessageBox.information(
                        self, "Info", f"Postać {char_table_name} już jest w trackerze."
                    )
                    return

            initiative_value = 10

            initiative, ok = QInputDialog.getInt(
                self,
                "Inicjatywa",
                f"Inicjatywa dla {char_table_name}:",
                value=initiative_value,
                minValue=self.INITIATIVE_RANGE[0],
                maxValue=self.INITIATIVE_RANGE[1],
            )

            if ok:
                self.add_character_data(char_table_name, initiative, self.STATUSES[0])

    def remove_character_data(self, row: int):
        """Remove a character from the initiative table.

        Removes the specified row from the table and adjusts the current
        turn index if necessary to maintain valid state.

        Args:
            row (int): The row index to remove
        """
        if 0 <= row < self.table.rowCount():
            self.table.removeRow(row)
            if self.current_turn >= self.table.rowCount():
                self.current_turn = self.table.rowCount() - 1
            self.update_row_highlighting()

    def remove_character(self):
        """Remove the currently selected character with confirmation.

        Prompts the user for confirmation before removing the selected
        character from the initiative tracker. Shows appropriate messages
        if no character is selected.
        """
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
        """Advance to the next living character's turn.

        Cycles through characters in initiative order, automatically
        skipping characters that are not alive (stunned or dead).
        Shows a message if no living characters remain.
        """
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
        """Get the status of a character at the specified table row.

        Args:
            row (int): The table row index

        Returns:
            str: The character's status, or 'Martwy' (Dead) if row is invalid
        """
        if row < 0 or row >= self.table.rowCount():
            return self.STATUSES[2]  # "Martwy" - changed from [3] to [2]
        status_item = self.table.item(row, 2)
        return status_item.text() if status_item else self.STATUSES[0]

    def update_row_highlighting(self):
        """Update visual highlighting to show the current turn.

        Highlights the row of the character whose turn it currently is
        and removes highlighting from all other rows.
        """
        for row in range(self.table.rowCount()):
            if row == self.current_turn:
                self.highlight_row(row)
            else:
                self.dehighlight_row(row)

    def highlight_row(self, row: int):
        """Apply visual highlighting to a table row.

        Makes the text bold, italic, and underlined to indicate
        the current active character.

        Args:
            row (int): The table row index to highlight
        """
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
        """Remove visual highlighting from a table row.

        Resets text formatting to normal (removes bold, italic, underline).

        Args:
            row (int): The table row index to dehighlight
        """
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
        """Sort characters by initiative value and status.

        Sorts characters in descending order by initiative value,
        with alive characters prioritized over stunned/dead ones
        when initiative values are equal. Resets the current turn
        to the first character after sorting.
        """
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
        """Handle widget resize events for responsive UI.

        Switches between text and icon-only button layouts based
        on available width to maintain usability on smaller screens.

        Args:
            event: The resize event
        """
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
        """Update button icon colors when theme changes.

        Updates the icon colors for all buttons when in icon-only mode
        to match the current theme.

        Args:
            icon_color: The new icon color to apply
        """
        if self.table.width() < self.BUTTONS_RESIZE_THRESHOLD:
            for btn in [self.next_btn, self.add_btn, self.remove_btn, self.sort_btn]:
                btn.setIcon(qta.icon(btn.icon_name, color=icon_color))


def build() -> InitiativeTracker:
    """Factory function to create an InitiativeTracker widget.

    Returns:
        InitiativeTracker: A fully configured initiative tracker widget
    """
    return InitiativeTracker()
