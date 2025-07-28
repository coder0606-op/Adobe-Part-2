FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

RUN curl -L -o model.onnx https://huggingface.co/onnx-models/paraphrase-multilingual-MiniLM-L12-v2-onnx/resolve/main/model.onnx


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


CMD ["python", "main.py"]
