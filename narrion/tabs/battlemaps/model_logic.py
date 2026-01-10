"""Battlemap CLIP Model Logic.

This module handles the initialization, downloading, and inference of the ONNX-based
CLIP model used for semantic search of battlemaps. It provides a unified interface
for converting both images and text into normalized vector embeddings.

The module manages:
- Automatic downloading of model files from HuggingFace
- ONNX Runtime session initialization for CPU execution
- Image preprocessing and embedding generation
- Text tokenization and embedding generation
"""

from pathlib import Path

from huggingface_hub import snapshot_download
import numpy as np
import onnxruntime as ort
from PIL import Image
from transformers import CLIPProcessor


class ModelLogic:
    """Manages the lifecycle and inference of the Battlemap CLIP model.

    This class handles downloading the model from HuggingFace if missing,
    loading the ONNX runtimes, and generating embeddings for both images and text.
    It uses separate ONNX sessions for image and text encoding to optimize resource usage.

    Attributes:
        repo_id (str): The HuggingFace repository ID where the model is stored.
        base_path (Path): Absolute local path to the model directory.
        processor (CLIPProcessor): The HuggingFace CLIP processor for input preparation.
        img_session (ort.InferenceSession): ONNX runtime session for image encoding.
        txt_session (ort.InferenceSession): ONNX runtime session for text encoding.
    """

    def __init__(self, model_folder: str = "onnx-clip"):
        """Initialize the ModelLogic instance.

        Sets up paths, ensures model files exist locally, and initializes
        the CLIP processor and ONNX inference sessions.

        Args:
            model_folder (str): Name of the subfolder within the 'models' directory
                where model files should be stored. Defaults to "onnx-clip".
        """
        self.repo_id = "Rpgshit/battlemap-clip-model"
        current_file_path = Path(__file__).resolve()
        # Assumes directory structure: root/module/file.py -> root/models/model_folder
        self.base_path = current_file_path.parents[3] / "models" / model_folder

        self.ensure_model_exists()

        self.processor = CLIPProcessor.from_pretrained(str(self.base_path), use_fast=False)

        sess_options = ort.SessionOptions()
        sess_options.log_severity_level = 3  # Error logging only

        self.img_session = ort.InferenceSession(
            str(self.base_path / "image_model.onnx"),
            sess_options,
            providers=["CPUExecutionProvider"],
        )
        self.txt_session = ort.InferenceSession(
            str(self.base_path / "text_model.onnx"),
            sess_options,
            providers=["CPUExecutionProvider"],
        )

    def ensure_model_exists(self):
        """Verify local model existence and download if necessary.

        Checks if the base path and required ONNX files exist. If any are missing,
        downloads the entire repository snapshot from HuggingFace to the local directory.
        """
        required_files = ["image_model.onnx", "text_model.onnx"]
        missing = False

        if not self.base_path.exists():
            missing = True
        else:
            for f in required_files:
                if not (self.base_path / f).exists():
                    missing = True
                    break

        if missing:
            snapshot_download(
                repo_id=self.repo_id, local_dir=self.base_path, local_dir_use_symlinks=False
            )

    def process_image(self, image_path: str | Path) -> np.ndarray:
        """Generate a normalized embedding vector for a given image.

        Args:
            image_path (str | Path): File path to the image to be processed.

        Returns:
            np.ndarray: A normalized numpy array representing the image embedding.
                The shape is (1, embedding_dimension).
        """
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="np", padding=True)
        pixel_values = inputs["pixel_values"].astype(np.float32)

        outputs = self.img_session.run(["image_embeddings"], {"pixel_values": pixel_values})
        emb = outputs[0]
        # Normalize the embedding
        return emb / np.linalg.norm(emb, axis=1, keepdims=True)

    def process_text(self, text: str) -> np.ndarray:
        """Generate a normalized embedding vector for a given text query.

        Args:
            text (str): The search query or description to be processed.

        Returns:
            np.ndarray: A normalized numpy array representing the text embedding.
                The shape is (1, embedding_dimension).
        """
        inputs = self.processor(
            text=[text], return_tensors="np", padding="max_length", max_length=77, truncation=True
        )

        outputs = self.txt_session.run(
            ["text_embeddings"],
            {
                "input_ids": inputs["input_ids"].astype(np.int64),
                "attention_mask": inputs["attention_mask"].astype(np.float32),
            },
        )
        emb = outputs[0]
        # Normalize the embedding
        return emb / np.linalg.norm(emb, axis=1, keepdims=True)
