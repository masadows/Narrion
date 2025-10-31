from collections import defaultdict
from itertools import chain
import os
import random

from PySide6.QtGui import QIcon
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


def build() -> QWidget:
    w = QWidget()
    v = QVBoxLayout(w)
    v.setContentsMargins(6, 6, 6, 6)

    qss_path = os.path.join(os.path.dirname(__file__), "dice_roller.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            w.setStyleSheet(f.read())

    # v.addWidget(SectionHeader("Rzut kośćmi"))

    log = QPlainTextEdit()
    log.setObjectName("logBox")
    log.setReadOnly(True)
    log.setPlainText("Log rzutów...")
    v.addWidget(log)

    roller_group = QGroupBox("🎲 Roller kości")
    roller_group.setObjectName("rollerGroup")
    roller_group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    grid = QGridLayout(roller_group)

    dice_types = [2, 4, 6, 8, 10, 12, 20, 100]
    selected_dices = defaultdict(int)
    modifier = {"val": 0}

    icons_path = os.path.join(os.path.dirname(__file__), "icons")
    for i, sides in enumerate(dice_types):
        btn = QPushButton()
        btn.setProperty("diceButton", True)
        btn.setFixedSize(70, 60)

        icon_path = os.path.join(icons_path, f"d{sides}.svg")
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(btn.size() * 0.8)

        btn.clicked.connect(
            lambda _, s=sides: (
                selected_dices.update([(s, selected_dices[s] + 1)]),
                update_label(),
            )
        )
        grid.addWidget(btn, i // 4, i % 4)

    label = QLabel()
    label.setObjectName("countLabel")
    label.setWordWrap(True)
    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    grid.addWidget(label, 4, 0, 2, 3)

    def update_label():
        text = " + ".join([f"{v}d{k}" for k, v in selected_dices.items() if v > 0])
        if modifier["val"] != 0:
            text += f"{modifier['val']:+d}"
        label.setText(text)

    def adjust_mod(delta):
        modifier["val"] += delta
        update_label()

    mod_minus = QPushButton("-")
    mod_plus = QPushButton("+")
    mod_minus.setProperty("smallButton", True)
    mod_plus.setProperty("smallButton", True)

    mod_minus.clicked.connect(lambda: adjust_mod(-1))
    mod_plus.clicked.connect(lambda: adjust_mod(1))

    grid.addWidget(QLabel("Bonus:"), 3, 0)
    grid.addWidget(mod_minus, 3, 1)
    grid.addWidget(mod_plus, 3, 2)

    reset_btn = QPushButton("RESET")
    reset_btn.setProperty("resetButton", True)
    reset_btn.clicked.connect(lambda: reset(selected_dices, modifier, update_label, log))
    grid.addWidget(reset_btn, 5, 3)

    roll_btn2 = QPushButton("Rzuć!")
    roll_btn2.setObjectName("rollButton")
    roll_btn2.clicked.connect(lambda: roll(selected_dices, modifier["val"], log))
    grid.addWidget(roll_btn2, 6, 0, 1, 4)

    update_label()
    v.addWidget(roller_group)

    return w


def reset(selected_dices, modifier, update_label, log):
    for k, _ in selected_dices.items():
        selected_dices[k] = 0
    modifier["val"] = 0
    update_label()
    log.appendPlainText("Zresetowano ustawienia.")


def roll(selected_dices, modifier, log):
    rolls = [
        ([random.randint(1, k) for _ in range(v)]) for k, v in selected_dices.items() if v > 0
    ]
    total = sum(flatten(rolls)) + modifier
    roll = "+".join([f"{v}d{k}" for k, v in selected_dices.items() if v > 0])
    if modifier != 0:
        roll += f"{modifier:+d}"
    log.appendPlainText(f"Rzut {roll}: {str(rolls)} => {total}")


def flatten(list_of_lists):
    "Flatten one level of nesting."
    return chain.from_iterable(list_of_lists)
