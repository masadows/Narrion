from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from widgets.section_header import SectionHeader


def build() -> QWidget:
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(6, 6, 6, 6)

    left = QVBoxLayout()
    left.addWidget(SectionHeader("Baza NPC"))
    npc_list = QListWidget()
    npc_list.addItems(["Kupiec Tom", "Strażnik Miejski", "Mistrz Kowalstwa"])
    left.addWidget(npc_list)
    left.addWidget(QPushButton("Nowy NPC"))
    left.addWidget(QPushButton("Importuj postać"))

    right = QVBoxLayout()
    right.addWidget(SectionHeader("Szczegóły NPC"))
    form = QFormLayout()
    form.addRow("Imię:", QLineEdit())
    form.addRow("Rola:", QComboBox())
    form.addRow("Opis:", QTextEdit())
    right.addLayout(form)
    right.addStretch()

    h.addLayout(left, 1)
    h.addLayout(right, 2)
    return w
