"""Responsive Image Display Widget.

This module provides a custom implementation of a QLabel designed to display
images that automatically resize to fit their container while maintaining
their original aspect ratio. This addresses the standard QLabel limitation
where setPixmap() forces a fixed size or clips the image.
"""

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy


class ScalableImageLabel(QLabel):
    """A QLabel that scales its pixmap content to fill the available space.

    This widget automatically adjusts the displayed image size whenever the
    widget itself is resized (e.g., when the window is maximized or splitters
    are moved). It maintains the image's aspect ratio and uses smooth
    transformation for high-quality downscaling.

    Attributes:
        _pixmap (QPixmap | None): The original, full-resolution image data.
            Used as the source for generating scaled previews.
    """

    def __init__(self, placeholder_text: str = ""):
        """Initialize the scalable label.

        Sets the size policy to `Ignored` to prevent the pixmap's original size
        from forcing the widget's minimum size (allowing it to shrink).

        Args:
            placeholder_text (str): Text to display when no image is loaded.
        """
        super().__init__(placeholder_text)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self._pixmap = None

    def set_image(self, path: str):
        """Load an image from a file path and display it.

        Args:
            path (str): The absolute or relative path to the image file.
                If the path is invalid or None, the placeholder text is shown.
        """
        if path and os.path.exists(path):
            self._pixmap = QPixmap(path)
            self.update_view()
        else:
            self._pixmap = None
            self.setText("Brak podglądu")

    def resizeEvent(self, event):
        """Handle widget resize events to trigger image re-scaling.

        Args:
            event (QResizeEvent): The resize event containing old and new dimensions.
        """
        if self._pixmap:
            self.update_view()
        super().resizeEvent(event)

    def update_view(self):
        """Scale the internal pixmap to fit the current widget dimensions.

        The result is set as the label's visible pixmap.
        """
        if not self._pixmap:
            return

        scaled = self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        super().setPixmap(scaled)
