"""Theme Loader and Management Module.

This module is responsible for discovering, loading, and managing application themes
defined in QSS (Qt Style Sheets) files. It automatically scans the directory
containing this script for `.qss` files and constructs a registry of available themes.

The module implements a custom metadata extraction mechanism that reads specific
comments within the QSS files to determine dynamic properties, such as the
color used for recoloring SVG icons to match the theme.

Attributes:
    THEMES (dict): A dictionary registry of available themes.
        Key: Human-readable theme name (str).
        Value: Dict containing 'path' (str) and 'icon_color' (QColor).
    DEFAULT_FONT (dict): The configuration of the default loaded theme.
        Contains 'name' and 'icon_color'.
"""

from pathlib import Path

from PySide6.QtGui import QColor

THEMES = {}
theme_folder = Path(__file__).parent


def get_icon_color_from_qss(path: Path | str) -> str:
    """Extract the icon color definition from a QSS file.

    Parses the given file line by line looking for a CSS-style comment containing
    the 'icon-color' key. This allows the QSS file to define not just widget styles,
    but also how SVG icons should be programmatically recolored.

    Expected format in QSS:
    `/* icon-color: #RRGGBB; */`

    Args:
        path (Path | str): The file path to the QSS stylesheet.

    Returns:
        str: The hex color code string (e.g., "#ff0000").
             Returns "#ffffff" (white) if no definition is found.
    """
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("/*") and "icon-color:" in line:
                color = line.split("icon-color:")[1].split(";")[0].strip()
                return color
    return "#ffffff"


for qss_file in theme_folder.glob("*.qss"):
    name = qss_file.stem.replace("_", " ").title()
    THEMES[name] = {"path": str(qss_file), "icon_color": QColor(get_icon_color_from_qss(qss_file))}

_key, _value = next(iter(THEMES.items()))
DEFAULT_FONT = dict(name=_key, icon_color=_value["icon_color"])
