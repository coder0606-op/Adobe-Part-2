import os
import json
import logging
from pathlib import Path

from pdf_extractor import extract_chunks_from_pdf
from semantic_ranker import rank_chunks_by_relevance, format_output
from outline_generator import generate_outline

logging.basicConfig(level=logging.INFO, format="🔹 [%(levelname)s] %(message)s")

INPUT_DIR = "input"
OUTPUT_DIR = "output"
INPUT_JSON_PATH = os.path.join(INPUT_DIR, "challenge.json")
RESULT_PATH = os.path.join(OUTPUT_DIR, "result.json")

def load_input_json():
    if not os.path.exists(INPUT_JSON_PATH):
        logging.error("❌ input.json not found in input directory.")
        return None
    try:
        with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"❌ Failed to load input.json: {e}")
        return None

def main():
    metadata = load_input_json()
    if not metadata:
        return

    documents = metadata.get("documents", [])
    persona = metadata.get("persona", {}).get("role", "Unknown Persona")
    job = metadata.get("job_to_be_done", {}).get("task", "No job specified")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_chunks = []

    for doc in documents:
        filename = doc.get("filename")
        if not filename:
            logging.warning("⚠️ Skipping document without filename.")
            continue

        input_pdf_path = os.path.join(INPUT_DIR, filename)
        if not os.path.exists(input_pdf_path):
            logging.warning(f"⚠️ PDF file not found: {input_pdf_path}")
            continue

        try:
            outline = generate_outline(input_pdf_path)
            chunks = extract_chunks_from_pdf(input_pdf_path,outline=outline)

            for chunk in chunks:
                chunk["document"] = filename

            all_chunks.extend(chunks)

            logging.info(f"✅ Extracted {len(chunks)} chunks from {filename}")

        except Exception as e:
            logging.error(f"❌ Failed processing {filename}: {e}")

    if not all_chunks:
        logging.warning("⚠️ No chunks extracted from any document. Exiting.")
        return

    top_chunks = rank_chunks_by_relevance(all_chunks, persona, job, top_k=1)
    top_chunk = top_chunks[0] if top_chunks else {}

    input_docs = sorted({c.get("document", "Unknown") for c in all_chunks})
    result = format_output(input_docs, persona, job, [top_chunk])

    try:
        with open(RESULT_PATH, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logging.info(f"🎯 Final output written to {RESULT_PATH}")
    except Exception as e:
        logging.error(f"❌ Failed to write result.json: {e}")

if __name__ == "__main__":
    logging.info("🚀 Starting processing pipeline")
    main()
