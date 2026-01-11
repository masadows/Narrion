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

