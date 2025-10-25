from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel


class SectionHeader(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        f = QFont()
        f.setPointSize(11)
        f.setBold(True)
        self.setFont(f)
