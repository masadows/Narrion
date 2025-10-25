import os

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from widgets.section_header import SectionHeader


def build() -> QWidget:
    w = QWidget()
    v = QVBoxLayout(w)
    v.setContentsMargins(6, 6, 6, 6)

    v.addWidget(SectionHeader("Tracker inicjatywy"))

    table = QTableWidget(0, 3)
    table.setHorizontalHeaderLabels(["Nazwa", "Inicjatywa", "Status"])
    for row, item in enumerate([("Aldren", "18", "Żywy"), ("Szablozębny", "12", "Żywy")]):
        table.insertRow(row)
        for col, val in enumerate(item):
            table.setItem(row, col, QTableWidgetItem(val))
    v.addWidget(table)

    controls = QHBoxLayout()
    controls.addWidget(QPushButton("Dodaj uczestnika"))
    controls.addWidget(QPushButton("Usuń"))
    controls.addStretch()

    btn = QPushButton()
    image_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../icones/next-button.svg"
    )
    btn.setIcon(QIcon(image_path))
    btn.setIconSize(QSize(20, 20))
    controls.addWidget(btn)
    v.addLayout(controls)

    return w
