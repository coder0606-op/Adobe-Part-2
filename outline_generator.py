import fitz  # PyMuPDF
from typing import List, Dict

def generate_outline(pdf_path: str) -> List[Dict]:
    """
    Extracts the outline (table of contents) from the given PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        List[Dict]: A list of outline entries, each with 'level', 'text', and 'page'.
    """
    outline_result = []

    try:
        doc = fitz.open(pdf_path)
        toc = doc.get_toc(simple=True)

        if not toc:
            print(f"[WARN] No outline found in {pdf_path}")
            return outline_result

        for entry in toc:
            level, title, page = entry
            outline_result.append({
                "level": f"H{min(level, 3)}",  # Optional: cap nesting
                "text": title.strip(),
                "page": page
            })

        outline_result.sort(key=lambda x: x["page"])  # Optional: ensure ordering

    except Exception as e:
        print(f"[ERROR] Failed to extract outline from {pdf_path}: {e}")

    return outline_result
