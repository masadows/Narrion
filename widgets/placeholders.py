from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont

def make_placeholder(title: str, subtitle: str = '') -> QWidget:
    w = QWidget()
    v = QVBoxLayout(w)
    v.setContentsMargins(8, 8, 8, 8)
    title_label = QLabel(title)
    title_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
    subtitle_label = QLabel(subtitle)
    subtitle_label.setStyleSheet('color: #bfbfbf;')
    subtitle_label.setWordWrap(True)
    v.addWidget(title_label)
    if subtitle:
        v.addWidget(subtitle_label)
    v.addStretch()
    return w
