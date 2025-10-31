from pathlib import Path

from PySide6.QtGui import QColor

THEMES = {}
theme_folder = Path(__file__).parent


def get_icon_color_from_qss(path):
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
