from unittest.mock import MagicMock, patch
import pytest
import numpy as np

from narrion.tabs.battlemaps.model_logic import ModelLogic


@pytest.fixture
def mock_dependencies():
    with (
        patch("narrion.tabs.battlemaps.model_logic.snapshot_download") as mock_download,
        patch("narrion.tabs.battlemaps.model_logic.ort.InferenceSession") as mock_ort,
        patch("narrion.tabs.battlemaps.model_logic.CLIPProcessor") as mock_processor,
        patch("narrion.tabs.battlemaps.model_logic.Image") as mock_image,
        patch("pathlib.Path.exists") as mock_exists,
    ):
        yield {
            "download": mock_download,
            "ort": mock_ort,
            "processor": mock_processor,
            "image": mock_image,
            "exists": mock_exists,
        }


class TestModelLogic:
    def test_init_downloads_model_if_missing(self, mock_dependencies):
        mock_dependencies["exists"].return_value = False

        model = ModelLogic()

        mock_dependencies["download"].assert_called_once()
        assert model.repo_id == "Rpgshit/battlemap-clip-model"

    def test_init_skips_download_if_present(self, mock_dependencies):
        mock_dependencies["exists"].return_value = True

        ModelLogic()

        mock_dependencies["download"].assert_not_called()

    def test_sessions_initialized_correctly(self, mock_dependencies):
        mock_dependencies["exists"].return_value = True

        model = ModelLogic()
        mock_dependencies["processor"].from_pretrained.assert_called_once()

        assert mock_dependencies["ort"].call_count == 2

    def test_process_image(self, mock_dependencies):
        mock_dependencies["exists"].return_value = True

        mock_processor_instance = mock_dependencies["processor"].from_pretrained.return_value
        mock_processor_instance.return_value = {
            "pixel_values": np.zeros((1, 3, 224, 224), dtype=np.float32)
        }

        mock_img_session = mock_dependencies["ort"].return_value
        mock_img_session.run.return_value = [np.array([[10.0, 0.0]], dtype=np.float32)]

        model = ModelLogic()

        result = model.process_image("fake_path.jpg")

        mock_dependencies["image"].open.assert_called_with("fake_path.jpg")
        mock_img_session.run.assert_called_once()

        expected = np.array([[1.0, 0.0]], dtype=np.float32)
        np.testing.assert_array_almost_equal(result, expected)

    def test_process_text(self, mock_dependencies):
        mock_dependencies["exists"].return_value = True

        mock_processor_instance = mock_dependencies["processor"].from_pretrained.return_value
        mock_processor_instance.return_value = {
            "input_ids": np.zeros((1, 77), dtype=np.int64),
            "attention_mask": np.zeros((1, 77), dtype=np.float32),
        }
        model = ModelLogic()

        mock_txt_session = MagicMock()
        mock_txt_session.run.return_value = [np.array([[0.0, 5.0]], dtype=np.float32)]
        model.txt_session = mock_txt_session

        result = model.process_text("a dark dungeon")

        mock_processor_instance.assert_called_with(
            text=["a dark dungeon"],
            return_tensors="np",
            padding="max_length",
            max_length=77,
            truncation=True,
        )
        mock_txt_session.run.assert_called_once()
        expected = np.array([[0.0, 1.0]], dtype=np.float32)
        np.testing.assert_array_almost_equal(result, expected)
