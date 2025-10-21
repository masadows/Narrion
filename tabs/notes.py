from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem, QPushButton, QTextEdit
from widgets.section_header import SectionHeader

def build() -> QWidget:
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(4, 4, 4, 4)

    left = QVBoxLayout()
    left.addWidget(SectionHeader('Notatki'))
    search = QLineEdit()
    search.setPlaceholderText('Szukaj notatek...')
    left.addWidget(search)

    tree = QTreeWidget()
    tree.setHeaderHidden(True)
    for folder in ('Lore', 'Lokacje', 'Zadania', 'NPC'):
        f = QTreeWidgetItem([folder])
        for i in range(3):
            child = QTreeWidgetItem([f'{folder} — Notatka {i+1}'])
            f.addChild(child)
        tree.addTopLevelItem(f)
    left.addWidget(tree)

    btns = QHBoxLayout()
    btns.addWidget(QPushButton('Nowa notatka'))
    btns.addWidget(QPushButton('Nowy folder'))
    left.addLayout(btns)

    right = QVBoxLayout()
    right.addWidget(SectionHeader('Edytor notatki'))
    editor = QTextEdit()
    editor.setPlaceholderText('Wybierz notatkę z lewej, aby zobaczyć zawartość...')
    right.addWidget(editor)

    h.addLayout(left, 1)
    h.addLayout(right, 2)
    return w
