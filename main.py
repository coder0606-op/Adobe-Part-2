import os
import json
import logging
from pathlib import Path

from pdf_extractor import extract_chunks_from_pdf
from semantic_ranker import rank_chunks_by_relevance, format_output
from outline_generator import extract_headings

logging.basicConfig(level=logging.INFO, format="🔹 [%(levelname)s] %(message)s")

BASE_DIR = "collection"
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
INPUT_JSON_PATH = os.path.join(BASE_DIR, "challenge1b_input.json")
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, "challenge1b_output.json")



def load_input_json():
    if not os.path.exists(INPUT_JSON_PATH):
        logging.error("❌ Input JSON not found.")
        return None
    try:
        with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"❌ Failed to read input JSON: {e}")
        return None

def main():
    metadata = load_input_json()
    if not metadata:
        return

    persona = metadata.get("persona", {}).get("role", "Unknown Persona")
    job = metadata.get("job_to_be_done", {}).get("task", "No job specified")

    all_results = []

    for filename in os.listdir(PDF_DIR):
        if not filename.lower().endswith(".pdf"):
            continue

        input_pdf_path = os.path.join(PDF_DIR, filename)

        try:
            outline = extract_headings(input_pdf_path)["outline"]
            chunks = extract_chunks_from_pdf(input_pdf_path, outline=outline)

            for chunk in chunks:
                chunk["document"] = filename

            if not chunks:
                logging.warning(f"⚠️ No chunks found in {filename}")
                continue

            top_chunks = rank_chunks_by_relevance(chunks, persona, job, top_k=1)
            top_chunk = top_chunks[0] if top_chunks else {}

            result = format_output([filename], persona, job, [top_chunk])
            all_results.append(result)

            logging.info(f"✅ Processed {filename} with {len(chunks)} chunks")

        except Exception as e:
            logging.error(f"❌ Failed processing {filename}: {e}")

    try:
        with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        logging.info(f"🎯 Final output written to {OUTPUT_JSON_PATH}")
    except Exception as e:
        logging.error(f"❌ Failed to write output JSON: {e}")

if __name__ == "__main__":
    logging.info("🚀 Starting document processing pipeline")
    main()
