import os
import json
from typing import List, Dict
from multiprocessing import Pool

from pdf_extractor import extract_chunks
from semantic_ranker import rank_chunks
from outline_generator import format_output


os.environ["TOKENIZERS_PARALLELISM"] = "false"

def process_pdfs(pdf_paths: List[str]) -> List[Dict]:
    with Pool(processes=min(4, len(pdf_paths))) as pool:
        results = pool.map(extract_chunks, pdf_paths)
    all_chunks = [chunk for result in results for chunk in result]
    print(f"Total chunks from all PDFs: {len(all_chunks)}")
    return all_chunks

def main(input_json_path: str, output_json_path: str):
    try:
        with open(input_json_path, "r") as f:
            input_data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading {input_json_path}: {str(e)}")
        return

    input_docs = [doc["filepath"] for doc in input_data.get("documents", [])]
    persona_raw = input_data.get("persona", "Unknown")
    job_raw = input_data.get("job_to_be_done", "Unknown")

    if isinstance(job_raw, dict):
        job = job_raw.get("task", "Unknown")
    elif isinstance(job_raw, str):
        job = job_raw
    else:
        print(f"⚠️ Unexpected format for job_to_be_done: {type(job_raw)}. Using string fallback.")
        job = str(job_raw)
    if isinstance(persona_raw, dict):
        persona = persona_raw.get("role", "Unknown")
    elif isinstance(persona_raw, str):
        persona = persona_raw
    else:
        print(f"⚠️ Unexpected format for persona: {type(persona_raw)}. Using string fallback.")
        persona = str(persona_raw)


    top_chunks = input_data.get("top_chunks", [])
    if not top_chunks:
        valid_docs = [doc for doc in input_docs if os.path.exists(doc)]
        if not valid_docs:
            print("❌ No valid PDF files found.")
            return
        print(f"📄 Processing {len(valid_docs)} PDFs: {valid_docs}")
        all_chunks = process_pdfs(valid_docs)
        top_chunks = rank_chunks(all_chunks, job)

    output = format_output(input_docs, persona, job, top_chunks)

    try:
        with open(output_json_path, "w") as f:
            json.dump(output, f, indent=4)
        print(f"✅ Output saved to {output_json_path}")
    except Exception as e:
        print(f"❌ Error saving output: {str(e)}")


if __name__ == "__main__":
    json_path = "collection/challenge1b_input.json"
    base_path = "collection/pdfs"

    with open(json_path, "r") as f:
        data = json.load(f)

    for doc in data.get("documents", []):
        doc["filepath"] = os.path.join(base_path, doc["filename"])

    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

    print("✅ Added full paths under 'filepath' in documents")

    input_path = "collection/challenge1b_input.json"
    output_path = "collection/challenge1b_output.json"

    main(input_path, output_path)
