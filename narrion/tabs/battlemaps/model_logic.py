from transformers import CLIPProcessor
import onnxruntime as ort
import numpy as np
from pathlib import Path
from PIL import Image


class ModelLogic:
    def __init__(self, model_folder="onnx-export"):
        current_file_path = Path(__file__).resolve()
        self.base_path = current_file_path.parents[3] / "models" /model_folder_name
        
        print(f"Szukam modelu w: {self.base_path}")
        
        if not self.base_path.exists():
            raise FileNotFoundError(f"Nie znaleziono folderu modelu: {self.base_path}")

        self.processor = CLIPProcessor.from_pretrained(str(self.base_path))
        
        sess_options = ort.SessionOptions()
        sess_options.log_severity_level = 3
        
        self.img_session = ort.InferenceSession(
            str(self.base_path / "image_model.onnx"), 
            sess_options, providers=['CPUExecutionProvider']
        )
        self.txt_session = ort.InferenceSession(
            str(self.base_path / "text_model.onnx"), 
            sess_options, providers=['CPUExecutionProvider']
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
            text=[text], 
            return_tensors="np", 
            padding="max_length", 
            max_length=77, 
            truncation=True
        )

        outputs = self.txt_session.run(
            ["text_embeddings"],
            {
                "input_ids": inputs["input_ids"].astype(np.int64),
                "attention_mask": inputs["attention_mask"].astype(np.float32) 
            }
        )
        emb = outputs[0]
        return emb / np.linalg.norm(emb, axis=1, keepdims=True)