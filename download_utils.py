

import os
import requests

def download_model_if_missing(model_path="model.onnx"):
    url = "https://huggingface.co/onnx-models/paraphrase-multilingual-MiniLM-L12-v2-onnx/resolve/main/model.onnx"

    if os.path.exists(model_path):
        print("✅ model.onnx already exists. Skipping download.")
        return

    print("🔽 model.onnx not found. Downloading from Hugging Face...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(model_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    print("✅ model.onnx downloaded successfully.")
