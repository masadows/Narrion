import os
from typing import List

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

import qtawesome as qta

from widgets.section_header import SectionHeader


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
        image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../icones/next-button.svg"
        )
        self.next_btn.setIcon(QIcon(image_path))
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
        name, ok = QInputDialog.getText(self, "Dodaj uczestnika", "Nazwa postaci:")

        if ok and name.strip():
            initiative, ok = QInputDialog.getInt(
                self,
                "Inicjatywa",
                f"Inicjatywa dla {name}:",
                value=10,
                minValue=self.INITIATIVE_RANGE[0],
                maxValue=self.INITIATIVE_RANGE[1],
            )

            if ok:
                self.add_character_data(name.strip(), initiative, self.STATUSES[0])

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
            return self.STATUSES[3]
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
            self.add_btn.setIcon(qta.icon("ei.plus"))
            self.remove_btn.setText("")
            self.remove_btn.setIcon(qta.icon("ei.minus"))
            self.sort_btn.setText("")
            self.sort_btn.setIcon(qta.icon("fa5s.sort"))
        else:
            self.add_btn.setIcon(QIcon())
            self.add_btn.setText("Dodaj uczestnika")
            self.remove_btn.setIcon(QIcon())
            self.remove_btn.setText("Usuń uczestnika")
            self.sort_btn.setIcon(QIcon())
            self.sort_btn.setText("Sortuj według inicjatywy")


def build() -> InitiativeTracker:
    """Build and return the initiative tracker widget."""
    return InitiativeTracker()
