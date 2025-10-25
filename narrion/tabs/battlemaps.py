from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from widgets.placeholders import make_placeholder
from widgets.section_header import SectionHeader


def build() -> QWidget:
    w = QWidget()
    v = QVBoxLayout(w)
    v.setContentsMargins(4, 4, 4, 4)

    header = QHBoxLayout()
    header.addWidget(SectionHeader("Battlemapy"))
    header.addStretch()
    header.addWidget(QPushButton("Dodaj ścieżkę"))
    header.addWidget(QPushButton("Skanuj folder"))
    v.addLayout(header)

    splitter = QSplitter(Qt.Horizontal)

    left_frame = QWidget()
    left_layout = QVBoxLayout(left_frame)
    left_layout.addWidget(QLabel("Lista map (z opisem)"))
    map_list = QListWidget()
    for i in range(1, 8):
        map_list.addItem(f"Mapa {i} — Ruiny nad rzeką")
    left_layout.addWidget(map_list)
    left_layout.addWidget(QPushButton("Dodaj do ulubionych"))

    right_frame = QWidget()
    right_layout = QVBoxLayout(right_frame)
    right_layout.addWidget(QLabel("Podgląd graficzny"))
    preview = make_placeholder("Podgląd mapy", "Miniatura mapy i meta-dane")
    # preview.setMinimumSize(360, 280)
    right_layout.addWidget(preview)

    splitter.addWidget(left_frame)
    splitter.addWidget(right_frame)
    splitter.setStretchFactor(1, 2)
    v.addWidget(splitter)

    search_h = QHBoxLayout()
    search_h.addWidget(QLabel("Wyszukaj po opisie (lokalny model ML):"))
    search_h.addWidget(QLineEdit())
    search_h.addWidget(QPushButton("Szukaj"))
    v.addLayout(search_h)

    return w
