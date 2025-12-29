import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy


class ScalableImageLabel(QLabel):
    def __init__(self, placeholder_text=""):
        super().__init__(placeholder_text)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self._pixmap = None

    def set_image(self, path):
        if path and os.path.exists(path):
            self._pixmap = QPixmap(path)
            self.update_view()
        else:
            self._pixmap = None
            self.setText("Brak podglądu")

    def resizeEvent(self, event):
        if self._pixmap:
            self.update_view()
        super().resizeEvent(event)

    def update_view(self):
        if not self._pixmap:
            return

        scaled = self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        super().setPixmap(scaled)
