from pathlib import Path

THEMES = {}
theme_folder = Path(__file__).parent

for qss_file in theme_folder.glob("*.qss"):
    name = qss_file.stem.replace("_", " ").title()
    THEMES[name] = str(qss_file)
