from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QLabel, QComboBox
from widgets.section_header import SectionHeader
from widgets.placeholders import make_placeholder
from PySide6.QtGui import QFont

def build() -> QWidget:
    w = QWidget()
    l = QHBoxLayout(w)
    l.setContentsMargins(4, 4, 4, 4)

    left = QVBoxLayout()
    left.addWidget(SectionHeader('Karty postaci'))
    char_list = QListWidget()
    char_list.addItems(['Aldren (Gracz)', 'Mira (Gracz)', 'Szablozębny (NPC)'])
    left.addWidget(char_list)
    left.addWidget(QPushButton('Dodaj kartę'))
    left.addWidget(QPushButton('Importuj PDF'))

    right = QVBoxLayout()
    right.addWidget(SectionHeader('Podgląd karty'))
    pdf_placeholder = make_placeholder('Podgląd PDF', 'Tutaj będzie miniatura lub viewer PDF')
    pdf_placeholder.setMinimumHeight(300)
    right.addWidget(pdf_placeholder)
    right.addWidget(QLabel('Przypisz do:'))
    assign = QComboBox()
    assign.addItems(['— brak —', 'Gracz: Aldren', 'Gracz: Mira', 'NPC: Szablozębny'])
    right.addWidget(assign)
    right.addStretch()

    l.addLayout(left, 1)
    l.addLayout(right, 2)
    return w
