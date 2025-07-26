# 🚀 Adobe Hackathon Submission - Multilingual PDF Processor

This project is a complete solution for the Adobe Hackathon Challenge. It ingests a structured `challenge.json` file and associated PDF documents, extracts relevant multilingual text, computes semantic similarity using a lightweight ONNX-based model, and generates a ranked output based on the job to be done.

---

## 📁 Project Structure

.
├── main.py # Entry script to run the solution
├── model.onnx # ONNX model (download manually)
│ extractor.py # PDF text extraction
│ embedder.py # Semantic embedder using ONNX
│ ranker.py # Cosine similarity-based ranking
├── input/ # Place your challenge.json and PDFs here
├── output/ # Outputs (answer.json, chunks.json)
├── .gitignore # Git ignore rules
└── README.md # This file

---

## ✅ Requirements

- Python 3.10+
- pip (Python package manager)
- Internet connection (only for first-time model download)
- Docker (optional)

---

## 📦 Install Dependencies

If you're running locally:

```bash
pip install -r requirements.txt


```

✅ All dependencies are lightweight. torch is not used.

wget https://huggingface.co/onnx-models/paraphrase-multilingual-MiniLM-L12-v2-onnx/resolve/main/model.onnx -O model.onnx

📂 Step 2: Setup Input & Output Folders
Create the input/ and output/ folders if they do not exist:

bash
Copy
Edit
mkdir input output
Place your challenge.json and all PDF files in the input/ folder like this:

pgsql
Copy
Edit
input/
├── challenge.json
├── doc1.pdf
├── doc2.pdf

Build the Docker image:

bash
Copy
Edit
docker build -t adobe-solution .

docker run --rm \
 -v $(pwd)/input:/app/input \
 -v $(pwd)/output:/app/output \
 adobe-solution
