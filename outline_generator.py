from datetime import datetime
from typing import List, Dict

def get_current_timestamp() -> str:
    return datetime.now().isoformat()

def format_output(input_docs: List[str], persona: str, job: str, top_chunks: List[Dict]) -> Dict:
    timestamp = get_current_timestamp()
    output = {
        "metadata": {
            "input_documents": input_docs,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": timestamp
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }
    for chunk in top_chunks:
        output["extracted_sections"].append({
            "document": chunk.get("document", "Unknown"),
            "page_number": chunk["page"],
            "section_title": chunk["section_title"],
            "importance_rank": chunk["importance_rank"]
        })
        output["subsection_analysis"].append({
            "document": chunk.get("document", "Unknown"),
            "refined_text": chunk["content"],
            "page_number": chunk["page"]
        })
    return output