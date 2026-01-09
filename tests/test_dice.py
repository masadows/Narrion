import pytest
from PySide6.QtWidgets import QApplication
import sys
from unittest.mock import MagicMock

mock_themes = MagicMock()
mock_themes.DEFAULT_FONT = {"icon_color": "#000000"}
sys.modules["themes"] = mock_themes
mock_widgets = MagicMock()


def fake_color_decorator(cls):
    return cls


mock_widgets.color_wrapper.color = fake_color_decorator
sys.modules["widgets"] = mock_widgets
sys.modules["widgets.color_wrapper"] = mock_widgets.color_wrapper

from narrion.tabs.dice.dice import DiceWidget, flatten


@pytest.fixture(scope="session")
def q_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def dice_logic(q_app, mocker):
    mocker.patch("os.path.exists", return_value=False)

    widget = DiceWidget()
    return widget


def test_flatten_logic():
    data = [[1, 2], [3], [], [4, 5]]
    result = list(flatten(data))
    assert result == [1, 2, 3, 4, 5]


def test_initial_data_state(dice_logic):
    assert dice_logic.modifier["val"] == 0
    assert len(dice_logic.selected_dices) == 0
    assert dice_logic.dice_types == [2, 4, 6, 8, 10, 12, 20, 100]


def test_manual_dice_selection(dice_logic):
    dice_logic.selected_dices[6] += 2
    dice_logic.selected_dices[20] += 1

    dice_logic.update_label()

    label_text = dice_logic.label.text()
    assert "2d6" in label_text
    assert "1d20" in label_text
    assert "+" in label_text


def test_modifier_logic(dice_logic):
    dice_logic.adjust_mod(5)
    assert dice_logic.modifier["val"] == 5
    assert "+5" in dice_logic.label.text()

    dice_logic.adjust_mod(-10)
    assert dice_logic.modifier["val"] == -5
    assert "-5" in dice_logic.label.text()


def test_reset_logic(dice_logic):
    dice_logic.selected_dices[8] = 10
    dice_logic.modifier["val"] = 99

    dice_logic.reset()

    assert dice_logic.modifier["val"] == 0
    assert dice_logic.selected_dices[8] == 0
    assert "Zresetowano" in dice_logic.log.toPlainText()


def test_roll_math_correctness(dice_logic, mocker):
    dice_logic.selected_dices[6] = 3
    dice_logic.modifier["val"] = 2

    mocker.patch("random.randint", side_effect=[1, 4, 6])

    dice_logic.roll()

    log_content = dice_logic.log.toPlainText().strip()
    last_line = log_content.split("\n")[-1]

    assert "=> 13" in last_line
    assert "1, 4, 6" in last_line or "4, 1, 6" in last_line
