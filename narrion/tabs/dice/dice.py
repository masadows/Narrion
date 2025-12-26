from collections import defaultdict
from itertools import chain
import os
import random

from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QIcon, QPainter, QColor
from PySide6.QtCore import QSize
from themes import DEFAULT_FONT
from widgets.color_wrapper import color


def create_colored_icon(icon_path: str, new_color: str | QColor, target_size: QSize) -> QIcon:
    if not os.path.exists(icon_path):
        return QIcon()
    base_icon = QIcon(icon_path)
    pixmap = base_icon.pixmap(target_size)

    if pixmap.isNull():
        return QIcon()

    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(new_color))
    painter.end()
    return QIcon(pixmap)


def flatten(list_of_lists):
    "Flatten one level of nesting."
    return chain.from_iterable(list_of_lists)


@color
class DiceWidget(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self)
        v.setContentsMargins(6, 6, 6, 6)

        qss_path = os.path.join(os.path.dirname(__file__), "dice_roller.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

        self.log = QPlainTextEdit()
        self.log.setObjectName("logBox")
        self.log.setReadOnly(True)
        self.log.setPlainText("Log rzutów...")
        v.addWidget(self.log)

        roller_group = QGroupBox("🎲 Roller kości")
        roller_group.setObjectName("rollerGroup")
        roller_group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        grid = QGridLayout(roller_group)

        self.dice_types = [2, 4, 6, 8, 10, 12, 20, 100]
        self.selected_dices = defaultdict(int)
        self.modifier = {"val": 0}

        self.buttons = list()
        icons_path = os.path.join(os.path.dirname(__file__), "icons")
        for i, sides in enumerate(self.dice_types):
            btn = QPushButton()
            btn.setProperty("diceButton", True)
            btn.setFixedSize(70, 60)

            icon_path = os.path.join(icons_path, f"d{sides}.svg")
            if os.path.exists(icon_path):
                size = btn.size() * 0.8
                colored_icon = create_colored_icon(icon_path, DEFAULT_FONT["icon_color"], size)
                btn.setIcon(colored_icon)
                btn.setIconSize(size)

            btn.clicked.connect(
                lambda _, s=sides: (
                    self.selected_dices.update([(s, self.selected_dices[s] + 1)]),
                    self.update_label(),
                )
            )
            btn.icon_path = icon_path
            self.buttons.append(btn)
            grid.addWidget(btn, i // 4, i % 4)

        self.label = QLabel()
        self.label.setObjectName("countLabel")
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid.addWidget(self.label, 4, 0, 2, 3)

        mod_minus = QPushButton("-")
        mod_plus = QPushButton("+")
        mod_minus.setProperty("smallButton", True)
        mod_plus.setProperty("smallButton", True)

        mod_minus.clicked.connect(lambda: self.adjust_mod(-1))
        mod_plus.clicked.connect(lambda: self.adjust_mod(1))

        grid.addWidget(QLabel("Bonus:"), 3, 0)
        grid.addWidget(mod_minus, 3, 1)
        grid.addWidget(mod_plus, 3, 2)

        reset_btn = QPushButton("RESET")
        reset_btn.setProperty("resetButton", True)
        reset_btn.clicked.connect(self.reset)
        grid.addWidget(reset_btn, 5, 3)

        roll_btn2 = QPushButton("Rzuć!")
        roll_btn2.setObjectName("rollButton")
        roll_btn2.clicked.connect(self.roll)
        grid.addWidget(roll_btn2, 6, 0, 1, 4)

        self.update_label()
        v.addWidget(roller_group)

    def update_label(self):
        text = " + ".join([f"{v}d{k}" for k, v in self.selected_dices.items() if v > 0])
        if self.modifier["val"] != 0:
            text += f"{self.modifier['val']:+d}"
        self.label.setText(text)

    def adjust_mod(self, delta):
        self.modifier["val"] += delta
        self.update_label()

    def reset(self):
        for k, _ in self.selected_dices.items():
            self.selected_dices[k] = 0
        self.modifier["val"] = 0
        self.update_label()
        self.log.appendPlainText("Zresetowano ustawienia.")

    def roll(self):
        rolls = [
            ([random.randint(1, k) for _ in range(v)])
            for k, v in self.selected_dices.items()
            if v > 0
        ]
        modifier = self.modifier["val"]
        total = sum(flatten(rolls)) + modifier
        roll = "+".join([f"{v}d{k}" for k, v in self.selected_dices.items() if v > 0])
        if modifier != 0:
            roll += f"{modifier:+d}"
        self.log.appendPlainText(f"Rzut {roll}: {str(rolls)} => {total}")

    def changeFontColor(self, icon_color):
        for btn in self.buttons:
            size = btn.iconSize()
            btn.setIcon(create_colored_icon(btn.icon_path, icon_color, size))


def build() -> QWidget:
    return DiceWidget()
