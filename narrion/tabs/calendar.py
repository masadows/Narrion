from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QCalendarWidget, QSplitter
from PySide6.QtCore import Qt

def build() -> QWidget:
    w = QWidget()
    v = QVBoxLayout(w)
    v.setContentsMargins(6, 6, 6, 6)

    title = QLabel("Terminarz sesji")
    title.setAlignment(Qt.AlignCenter)
    title.setMaximumHeight(40)
    
    v.addWidget(title)
    cal = QCalendarWidget()
    cal.setGridVisible(True)
    cal.setMinimumHeight(280)

    right = QVBoxLayout()
    right.addWidget(QLabel('Szczegóły wydarzeń'))
    right.addWidget(QLineEdit())
    right.addWidget(QTextEdit())
    right.addWidget(QPushButton('Synchronizuj z Google Calendar'))

    split = QSplitter(Qt.Horizontal)
    left_frame = QWidget()
    lf_layout = QVBoxLayout(left_frame)
    lf_layout.addWidget(cal)
    split.addWidget(left_frame)

    right_frame = QWidget()
    rf_layout = QVBoxLayout(right_frame)
    rf_layout.addLayout(right)
    split.addWidget(right_frame)
    split.setStretchFactor(0, 2)
    split.setStretchFactor(1, 1)

    v.addWidget(split)
    return w
