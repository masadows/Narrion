"""Standardized UI Header Component.

This module provides a reusable widget for creating consistent section titles
throughout the application's interface. It encapsulates specific font
settings (size and weight) to ensure visual uniformity without repeating
styling code in every widget.
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel


class SectionHeader(QLabel):
    """A bold, styled label used as a section title.

    Inherits from `QLabel` and automatically applies a predefined font style
    (11pt, Bold) upon initialization. This widget is intended to be used at
    the top of layout groups, lists, or distinct UI panels to denote hierarchy.



    Args:
        text (str): The title text to display.
    """

    def __init__(self, text: str):
        """Initialize the header with specific typography settings.

        Args:
            text (str): The string to be displayed as the header.
        """
        super().__init__(text)
        f = QFont()
        f.setPointSize(11)
        f.setBold(True)
        self.setFont(f)
