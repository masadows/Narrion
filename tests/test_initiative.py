import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
import tempfile
import sys

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QSpinBox,
    QTableWidgetItem,
    QDialog,
    QWidget,
    QLabel,
    QMessageBox,
)

# Mock the external modules before importing the module under test
mock_themes = MagicMock()
mock_themes.DEFAULT_FONT = {"icon_color": "#000000"}
sys.modules["themes"] = mock_themes

mock_widgets = MagicMock()


def fake_color_decorator(cls):
    return cls


def fake_section_header(*args, **kwargs):
    """Mock SectionHeader that returns a real QWidget."""
    return QLabel("Mocked Section Header")


mock_widgets.color_wrapper.color = fake_color_decorator
mock_widgets.section_header.SectionHeader = fake_section_header
sys.modules["widgets"] = mock_widgets
sys.modules["widgets.color_wrapper"] = mock_widgets.color_wrapper
sys.modules["widgets.section_header"] = mock_widgets.section_header

from narrion.tabs.initiative import (
    CharacterSelectionDialog,
    InitiativeItemDelegate,
    StatusItemDelegate,
    InitiativeTracker,
    build,
)


@pytest.fixture(scope="session")
def q_app():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_build_function(q_app):
    """Test the build factory function."""
    tracker = build()
    assert isinstance(tracker, InitiativeTracker)
    assert tracker.current_turn == -1
    assert tracker.table.rowCount() == 0


class TestCharacterSelectionDialog:
    """Test cases for CharacterSelectionDialog class."""

    @pytest.fixture
    def dialog(self, q_app):
        """Create a CharacterSelectionDialog instance for testing."""
        with patch("pathlib.Path.exists", return_value=False):
            return CharacterSelectionDialog()

    @pytest.fixture
    def dialog_with_campaigns(self, q_app):
        """Create a CharacterSelectionDialog with mocked campaigns."""
        with patch("pathlib.Path.exists", return_value=True), patch(
            "pathlib.Path.iterdir"
        ) as mock_iterdir:
            # Mock campaign directories
            mock_campaign = MagicMock()
            mock_campaign.name = "TestCampaign"
            mock_campaign.is_dir.return_value = True
            mock_iterdir.return_value = [mock_campaign]
            return CharacterSelectionDialog()

    def test_fallback_setup_ui(self, dialog):
        """Test fallback UI when no campaigns are available."""
        assert dialog.campaign_path is None
        assert dialog.manual_character_data is None
        assert dialog.windowTitle() == "Wybierz postać"
        assert dialog.isModal()

    def test_setup_ui_with_campaigns(self, dialog_with_campaigns):
        """Test UI setup when campaigns are available."""
        dialog = dialog_with_campaigns
        assert hasattr(dialog, "campaign_combo")
        assert hasattr(dialog, "type_combo")
        assert hasattr(dialog, "character_list")
        assert dialog.campaign_path is not None
        assert str(dialog.campaign_path).endswith("TestCampaign")

    def test_on_campaign_changed(self, dialog_with_campaigns):
        """Test campaign selection change."""
        dialog = dialog_with_campaigns
        dialog.on_campaign_changed("NewCampaign")
        assert str(dialog.campaign_path).endswith("NewCampaign")

    @patch("pathlib.Path.glob")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_load_characters_valid_json(self, mock_json_load, mock_file, mock_glob, dialog_with_campaigns):
        """Test loading characters from valid JSON files."""
        dialog = dialog_with_campaigns
        
        # Mock character files
        mock_file_path = MagicMock()
        mock_file_path.stem = "character1"
        mock_glob.return_value = [mock_file_path]
        
        # Mock character data
        mock_json_load.return_value = {
            "name": "Test Character",
            "short_description": "A test character"
        }
        
        # Mock the character directory exists
        with patch.object(Path, "exists", return_value=True):
            dialog.load_characters()
            
        assert dialog.character_list.count() == 1

    @patch("pathlib.Path.glob")
    def test_load_characters_invalid_json(self, mock_glob, dialog_with_campaigns):
        """Test loading characters with invalid JSON files."""
        dialog = dialog_with_campaigns
        
        # Mock character files
        mock_file_path = MagicMock()
        mock_file_path.stem = "character1"
        mock_glob.return_value = [mock_file_path]
        
        # Mock the character directory exists
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", side_effect=json.JSONDecodeError("msg", "doc", 0)):
            dialog.load_characters()
            
        # Should not add any items due to JSON error
        assert dialog.character_list.count() == 0

    @patch("narrion.tabs.initiative.QInputDialog.getText")
    @patch("narrion.tabs.initiative.QInputDialog.getInt")
    def test_add_manual_character_success(self, mock_get_int, mock_get_text, dialog):
        """Test successful manual character addition."""
        mock_get_text.return_value = ("Test Character", True)
        mock_get_int.return_value = (15, True)
        
        dialog.add_manual_character()
        
        assert dialog.manual_character_data is not None
        assert dialog.manual_character_data["name"] == "Test Character"
        assert dialog.manual_character_data["initiative"] == 15
        assert dialog.manual_character_data["status"] == InitiativeTracker.STATUSES[0]

    @patch("narrion.tabs.initiative.QInputDialog.getText")
    def test_add_manual_character_cancelled(self, mock_get_text, dialog):
        """Test cancelled manual character addition."""
        mock_get_text.return_value = ("", False)
        
        dialog.add_manual_character()
        
        assert dialog.manual_character_data is None

    def test_get_selected_character_data_no_selection(self, dialog_with_campaigns):
        """Test getting character data with no selection."""
        dialog = dialog_with_campaigns
        result = dialog.get_selected_character_data()
        assert result is None

    def test_get_selected_character_data_with_selection(self, dialog_with_campaigns):
        """Test getting character data with valid selection."""
        dialog = dialog_with_campaigns
        
        # Add a test item and select it
        dialog.type_combo.setCurrentText("Player")
        dialog.character_list.addItem("Test Character\nDescription")
        dialog.character_list.setCurrentRow(0)
        
        result = dialog.get_selected_character_data()
        assert result is not None
        assert result[0] == "Test Character"
        assert result[1] == "Player"


class TestInitiativeItemDelegate:
    """Test cases for InitiativeItemDelegate class."""

    @pytest.fixture
    def delegate(self, q_app):
        """Create an InitiativeItemDelegate instance for testing."""
        return InitiativeItemDelegate(min_value=1, max_value=30)

    def test_init_default_values(self, q_app):
        """Test delegate initialization with default values."""
        delegate = InitiativeItemDelegate()
        assert delegate.min_value == 1
        assert delegate.max_value == 30

    def test_init_custom_values(self, q_app):
        """Test delegate initialization with custom values."""
        delegate = InitiativeItemDelegate(min_value=5, max_value=50)
        assert delegate.min_value == 5
        assert delegate.max_value == 50

    def test_create_editor(self, delegate, q_app):
        """Test creating a QSpinBox editor."""
        from PySide6.QtWidgets import QWidget
        parent = QWidget()
        option = MagicMock()
        index = MagicMock()
        
        editor = delegate.createEditor(parent, option, index)
        
        assert isinstance(editor, QSpinBox)
        assert editor.minimum() == 1
        assert editor.maximum() == 30
        assert editor.alignment() == Qt.AlignCenter

    def test_set_editor_data(self, delegate, q_app):
        """Test setting data in the editor."""
        editor = QSpinBox()
        mock_index = MagicMock()
        mock_model = MagicMock()
        mock_model.data.return_value = "15"
        mock_index.model.return_value = mock_model
        
        delegate.setEditorData(editor, mock_index)
        
        assert editor.value() == 15

    def test_set_model_data(self, delegate, q_app):
        """Test setting model data from editor."""
        editor = QSpinBox()
        editor.setValue(20)
        mock_model = MagicMock()
        mock_index = MagicMock()
        
        delegate.setModelData(editor, mock_model, mock_index)
        
        mock_model.setData.assert_called_once_with(mock_index, 20, Qt.EditRole)

    def test_update_editor_geometry(self, delegate, q_app):
        """Test updating editor geometry."""
        from PySide6.QtCore import QRect
        editor = QSpinBox()
        mock_option = MagicMock()
        test_rect = QRect(10, 10, 100, 30)
        mock_option.rect = test_rect
        mock_index = MagicMock()
        
        delegate.updateEditorGeometry(editor, mock_option, mock_index)
        
        # Should call setGeometry with the option's rect
        assert editor.geometry() == test_rect


class TestStatusItemDelegate:
    """Test cases for StatusItemDelegate class."""

    @pytest.fixture
    def delegate(self, q_app):
        """Create a StatusItemDelegate instance for testing."""
        return StatusItemDelegate(statuses=["Żywy", "Ogłuszony", "Martwy"])

    def test_init_default_statuses(self, q_app):
        """Test delegate initialization with default statuses."""
        delegate = StatusItemDelegate()
        assert delegate.statuses == []

    def test_init_custom_statuses(self, delegate):
        """Test delegate initialization with custom statuses."""
        assert delegate.statuses == ["Żywy", "Ogłuszony", "Martwy"]

    def test_create_editor(self, delegate, q_app):
        """Test creating a QComboBox editor."""
        
        parent = QWidget()
        option = MagicMock()
        index = MagicMock()
        
        editor = delegate.createEditor(parent, option, index)
        
        assert isinstance(editor, QComboBox)
        assert editor.count() == 3

    def test_set_editor_data(self, delegate, q_app):
        """Test setting data in the editor."""
        editor = QComboBox()
        editor.addItems(["Żywy", "Ogłuszony", "Martwy"])
        mock_index = MagicMock()
        mock_model = MagicMock()
        mock_model.data.return_value = "Ogłuszony"
        mock_index.model.return_value = mock_model
        
        delegate.setEditorData(editor, mock_index)
        
        assert editor.currentText() == "Ogłuszony"

    def test_set_model_data(self, delegate, q_app):
        """Test setting model data from editor."""
        editor = QComboBox()
        editor.addItems(["Żywy", "Ogłuszony", "Martwy"])
        editor.setCurrentText("Martwy")
        mock_model = MagicMock()
        mock_index = MagicMock()
        
        delegate.setModelData(editor, mock_model, mock_index)
        
        mock_model.setData.assert_called_once_with(mock_index, "Martwy", Qt.EditRole)

    def test_update_editor_geometry(self, delegate, q_app):
        """Test updating editor geometry."""
        from PySide6.QtCore import QRect
        editor = QComboBox()
        mock_option = MagicMock()
        test_rect = QRect(20, 20, 150, 40)
        mock_option.rect = test_rect
        mock_index = MagicMock()
        
        delegate.updateEditorGeometry(editor, mock_option, mock_index)
        
        # Should call setGeometry with the option's rect
        assert editor.geometry() == test_rect


class TestInitiativeTracker:
    """Test cases for InitiativeTracker class."""

    @pytest.fixture
    def tracker(self, q_app):
        """Create an InitiativeTracker instance for testing."""
        return InitiativeTracker()

    def test_init(self, tracker):
        """Test InitiativeTracker initialization."""
        assert tracker.current_turn == -1
        assert tracker.table.rowCount() == 0
        assert tracker.table.columnCount() == 3
        assert tracker.STATUSES == ["Żywy", "Ogłuszony", "Martwy"]
        assert tracker.INITIATIVE_RANGE == (0, 1000)

    def test_class_constants(self):
        """Test class constants are properly defined."""
        assert InitiativeTracker.STATUSES == ["Żywy", "Ogłuszony", "Martwy"]
        assert InitiativeTracker.INITIATIVE_RANGE == (0, 1000)
        assert InitiativeTracker.BUTTONS_RESIZE_THRESHOLD == 450

    def test_add_character_data(self, tracker):
        """Test adding character data to the table."""
        tracker.add_character_data("Test Character", 15, "Żywy")
        
        assert tracker.table.rowCount() == 1
        assert tracker.table.item(0, 0).text() == "Test Character"
        assert tracker.table.item(0, 1).text() == "15"
        assert tracker.table.item(0, 2).text() == "Żywy"

    def test_remove_character_data(self, tracker):
        """Test removing character data from the table."""
        tracker.add_character_data("Test Character", 15, "Żywy")
        assert tracker.table.rowCount() == 1

        tracker.remove_character_data(0)
        assert tracker.table.rowCount() == 0

    def test_remove_character_data_invalid_row(self, tracker):
        """Test removing character data with invalid row index."""
        tracker.add_character_data("Test Character", 15, "Żywy")
        initial_count = tracker.table.rowCount()
        
        # Test invalid indices
        tracker.remove_character_data(-1)
        assert tracker.table.rowCount() == initial_count
        
        tracker.remove_character_data(999)
        assert tracker.table.rowCount() == initial_count

        tracker.remove_character_data(initial_count)
        assert tracker.table.rowCount() == initial_count

    def test_remove_character_data_adjust_current_turn(self, tracker):
        """Test that current_turn is adjusted when removing characters."""
        tracker.add_character_data("Character 1", 20, "Żywy")
        tracker.add_character_data("Character 2", 15, "Żywy")
        tracker.current_turn = 1
        
        # Remove the last character
        tracker.remove_character_data(1)
        
        assert tracker.current_turn == 0  # Should be adjusted

    def test_remove_character_data_current_turn_no_adjust(self, tracker):
        """Test that current_turn is not adjusted when removing other characters."""
        tracker.add_character_data("Character 1", 20, "Żywy")
        tracker.add_character_data("Character 2", 15, "Żywy")
        tracker.current_turn = 0
        
        # Remove the second character
        tracker.remove_character_data(1)
        
        assert tracker.current_turn == 0  # Should remain the same

    def test_get_character_status(self, tracker):
        """Test getting character status."""
        tracker.add_character_data("Test Character", 15, "Ogłuszony")
        
        assert tracker.get_character_status(0) == "Ogłuszony"
        assert tracker.get_character_status(-1) == "Martwy"  # Invalid row
        assert tracker.get_character_status(999) == "Martwy"  # Invalid row

    def test_next_turn_empty_table(self, tracker):
        """Test next turn with empty table."""
        initial_turn = tracker.current_turn
        tracker.next_turn()
        assert tracker.current_turn == initial_turn

    @patch.object(QMessageBox, 'information')
    def test_next_turn_single_alive_character(self, mock_message_box, tracker):
        """Test next turn with single alive character."""
        tracker.add_character_data("Alive Character", 20, "Żywy")
        tracker.current_turn = -1
        
        tracker.next_turn()
        
        assert tracker.current_turn == -1
        mock_message_box.assert_called_once()

    def test_next_turn_skip_dead_characters(self, tracker):
        """Test next turn skipping dead characters."""
        tracker.add_character_data("Dead Character", 20, "Martwy")
        tracker.add_character_data("Alive Character", 15, "Żywy")
        tracker.add_character_data("Stunned Character", 10, "Ogłuszony")
        tracker.current_turn = -1
        
        tracker.next_turn()
        
        assert tracker.current_turn == 1  # Should skip to alive character

    def test_next_turn_all_dead_characters(self, tracker):
        """Test next turn with all dead characters."""
        tracker.add_character_data("Dead Character 1", 20, "Martwy")
        tracker.add_character_data("Dead Character 2", 15, "Ogłuszony")
        
        with patch("narrion.tabs.initiative.QMessageBox.information") as mock_msg:
            tracker.next_turn()
            mock_msg.assert_called_once()
    
    def test_next_turn_cycling(self, tracker):
        """Test next turn cycling through characters."""
        tracker.add_character_data("Character 1", 20, "Żywy")
        tracker.add_character_data("Character 2", 15, "Żywy")
        tracker.current_turn = 0
        
        tracker.next_turn()
        assert tracker.current_turn == 1
        
        tracker.next_turn()
        assert tracker.current_turn == 0

    def test_sort_by_initiative_empty_table(self, tracker):
        """Test sorting with empty table."""
        tracker.sort_by_initiative()
        assert tracker.table.rowCount() == 0

    def test_sort_by_initiative_single_character(self, tracker):
        """Test sorting with single character."""
        tracker.add_character_data("Single Character", 15, "Żywy")
        tracker.sort_by_initiative()
        
        assert tracker.table.rowCount() == 1
        assert tracker.table.item(0, 0).text() == "Single Character"

    def test_sort_by_initiative_multiple_characters(self, tracker):
        """Test sorting multiple characters by initiative."""
        tracker.add_character_data("Low Initiative", 5, "Żywy")
        tracker.add_character_data("High Initiative", 20, "Żywy")
        tracker.add_character_data("Medium Initiative", 15, "Żywy")
        
        tracker.sort_by_initiative()
        
        # Should be sorted by descending initiative
        assert tracker.table.item(0, 0).text() == "High Initiative"
        assert tracker.table.item(1, 0).text() == "Medium Initiative"
        assert tracker.table.item(2, 0).text() == "Low Initiative"
        assert tracker.current_turn == 0

    def test_sort_by_initiative_with_status_priority(self, tracker):
        """Test sorting with status priority when initiatives are equal."""
        tracker.add_character_data("Dead Character", 15, "Martwy")
        tracker.add_character_data("Alive Character", 15, "Żywy")
        tracker.add_character_data("Stunned Character", 15, "Ogłuszony")
        
        tracker.sort_by_initiative()
        
        # With equal initiative, alive should come first, then stunned, then dead
        assert tracker.table.item(0, 2).text() == "Żywy"
        assert tracker.table.item(1, 2).text() == "Ogłuszony"
        assert tracker.table.item(2, 2).text() == "Martwy"

    def test_sort_by_initiative_mixed_statuses(self, tracker):
        """Test sorting with mixed statuses and initiatives."""
        tracker.add_character_data("Character A", 10, "Ogłuszony")
        tracker.add_character_data("Character B", 20, "Żywy")
        tracker.add_character_data("Character C", 15, "Martwy")
        tracker.add_character_data("Character D", 20, "Ogłuszony")
        
        tracker.sort_by_initiative()
        
        # Expected order:
        # Character B (20, Żywy)
        # Character D (20, Ogłuszony)
        # Character C (15, Martwy)
        # Character A (10, Ogłuszony)
        assert tracker.table.item(0, 0).text() == "Character B"
        assert tracker.table.item(1, 0).text() == "Character D"
        assert tracker.table.item(2, 0).text() == "Character C"
        assert tracker.table.item(3, 0).text() == "Character A"

    def test_highlight_row(self, tracker):
        """Test row highlighting."""
        tracker.add_character_data("Test Character", 15, "Żywy")
        
        tracker.highlight_row(0)
        
        item = tracker.table.item(0, 0)
        font = item.font()
        assert font.underline()
        assert font.bold()
        assert font.italic()

    def test_highlight_row_invalid_index(self, tracker):
        """Test highlighting invalid row index."""
        tracker.add_character_data("Test Character", 15, "Żywy")
        
        # Should not crash on invalid indices
        tracker.highlight_row(-1)
        tracker.highlight_row(999)

    def test_dehighlight_row(self, tracker):
        """Test row dehighlighting."""
        tracker.add_character_data("Test Character", 15, "Żywy")
        
        # First highlight, then dehighlight
        tracker.highlight_row(0)
        tracker.dehighlight_row(0)
        
        item = tracker.table.item(0, 0)
        font = item.font()
        assert not font.underline()
        assert not font.bold()
        assert not font.italic()

    def test_update_row_highlighting(self, tracker):
        """Test updating row highlighting."""
        tracker.add_character_data("Character 1", 20, "Żywy")
        tracker.add_character_data("Character 2", 15, "Żywy")
        tracker.current_turn = 1
        
        tracker.update_row_highlighting()
        
        # Character 2 should be highlighted
        item1 = tracker.table.item(0, 0)
        item2 = tracker.table.item(1, 0)
        
        assert not item1.font().bold()
        assert item2.font().bold()

    @patch("narrion.tabs.initiative.CharacterSelectionDialog")
    @patch("narrion.tabs.initiative.QInputDialog.getInt")
    @patch("narrion.tabs.initiative.QMessageBox.information")
    def test_add_character_manual(self, mock_msg, mock_get_int, mock_dialog_class, tracker):
        """Test adding character manually."""
        # Mock dialog instance
        mock_dialog = MagicMock()
        mock_dialog.exec.return_value = QDialog.Accepted
        mock_dialog.manual_character_data = {
            "name": "Manual Character",
            "initiative": 18,
            "status": "Żywy"
        }
        mock_dialog_class.return_value = mock_dialog
        
        tracker.add_character()
        
        assert tracker.table.rowCount() == 1
        assert tracker.table.item(0, 0).text() == "Manual Character"

    @patch("narrion.tabs.initiative.CharacterSelectionDialog")
    @patch("narrion.tabs.initiative.QInputDialog.getInt")
    @patch("narrion.tabs.initiative.QMessageBox.information")
    def test_add_character_duplicate_manual(self, mock_msg, mock_get_int, mock_dialog_class, tracker):
        """Test adding duplicate manual character."""
        # Add initial character
        tracker.add_character_data("Duplicate Character", 15, "Żywy")
        
        # Mock dialog for duplicate
        mock_dialog = MagicMock()
        mock_dialog.exec.return_value = QDialog.Accepted
        mock_dialog.manual_character_data = {
            "name": "Duplicate Character",
            "initiative": 18,
            "status": "Żywy"
        }
        mock_dialog_class.return_value = mock_dialog
        
        tracker.add_character()
        
        # Should still have only 1 character and show info message
        assert tracker.table.rowCount() == 1
        mock_msg.assert_called_once()

    @patch("narrion.tabs.initiative.CharacterSelectionDialog")
    def test_add_character_dialog_rejected(self, mock_dialog_class, tracker):
        """Test adding character when dialog is rejected."""
        mock_dialog = MagicMock()
        mock_dialog.exec.return_value = QDialog.Rejected
        mock_dialog_class.return_value = mock_dialog
        
        tracker.add_character()
        
        assert tracker.table.rowCount() == 0

    @patch("narrion.tabs.initiative.QMessageBox.question")
    def test_remove_character_confirmed(self, mock_question, tracker):
        """Test removing character with confirmation."""
        tracker.add_character_data("To Remove", 15, "Żywy")
        tracker.table.setCurrentCell(0, 0)
        mock_question.return_value = patch("narrion.tabs.initiative.QMessageBox.Yes").start()
        
        tracker.remove_character()
        
        assert tracker.table.rowCount() == 0

    @patch("narrion.tabs.initiative.QMessageBox.question")
    def test_remove_character_cancelled(self, mock_question, tracker):
        """Test removing character when cancelled."""
        tracker.add_character_data("Not Removed", 15, "Żywy")
        tracker.table.setCurrentCell(0, 0)
        mock_question.return_value = patch("narrion.tabs.initiative.QMessageBox.No").start()
        
        tracker.remove_character()
        
        assert tracker.table.rowCount() == 1

    @patch("narrion.tabs.initiative.QMessageBox.information")
    def test_remove_character_no_selection(self, mock_info, tracker):
        """Test removing character with no selection."""
        tracker.add_character_data("Character", 15, "Żywy")
        
        tracker.remove_character()
        
        mock_info.assert_called_once()
        assert tracker.table.rowCount() == 1

    def test_resize_event_narrow(self, tracker):
        """Test resize event with narrow width."""
        from PySide6.QtCore import QSize
        from PySide6.QtGui import QResizeEvent
        
        old_size = QSize(500, 300)
        new_size = QSize(400, 300)  # Below threshold
        resize_event = QResizeEvent(new_size, old_size)
        
        tracker.table.resize(400, 300)  # Below threshold
        
        tracker.resizeEvent(resize_event)
        
        # Buttons should have icons and no text
        assert tracker.add_btn.text() == ""
        assert tracker.remove_btn.text() == ""
        assert tracker.sort_btn.text() == ""

    def test_resize_event_wide(self, tracker):
        """Test resize event with wide width."""
        from PySide6.QtCore import QSize
        from PySide6.QtGui import QResizeEvent
        
        old_size = QSize(400, 300)
        new_size = QSize(500, 300)  # Above threshold
        resize_event = QResizeEvent(new_size, old_size)
        
        tracker.table.resize(500, 300)  # Above threshold
        
        tracker.resizeEvent(resize_event)
        
        # Buttons should have text and no icons
        assert "Dodaj" in tracker.add_btn.text()
        assert "Usuń" in tracker.remove_btn.text()
        assert "Sortuj" in tracker.sort_btn.text()