from pathlib import Path

from huggingface_hub import snapshot_download
import numpy as np
import onnxruntime as ort
from PIL import Image
from transformers import CLIPProcessor


class ModelLogic:
    def __init__(self, model_folder="onnx-clip"):
        self.repo_id = "Rpgshit/battlemap-clip-model"
        current_file_path = Path(__file__).resolve()
        self.base_path = current_file_path.parents[3] / "models" / model_folder

        self.ensure_model_exists()

        self.processor = CLIPProcessor.from_pretrained(str(self.base_path), use_fast=False)

        sess_options = ort.SessionOptions()
        sess_options.log_severity_level = 3

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

    def process_image(self, image_path):
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="np", padding=True)
        pixel_values = inputs["pixel_values"].astype(np.float32)

        outputs = self.img_session.run(["image_embeddings"], {"pixel_values": pixel_values})
        emb = outputs[0]
        return emb / np.linalg.norm(emb, axis=1, keepdims=True)

    def process_text(self, text):
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
        return emb / np.linalg.norm(emb, axis=1, keepdims=True)
