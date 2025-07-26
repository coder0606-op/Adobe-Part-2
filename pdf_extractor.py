import os
import fitz  
import logging
from typing import List, Dict, Optional

def extract_chunks_from_pdf(input_path: str, outline: Optional[List[Dict]] = None) -> List[Dict]:
    try:
        doc = fitz.open(input_path)

        if outline is None:
            outline = doc.get_toc(simple=True)

        if not outline:
            logging.warning(f"No outline found or provided for {input_path}. Skipping.")
            return []
        
        if outline and isinstance(outline[0], dict):
            outline = [
                (
                    int(item["level"].replace("H", "")),
                    item["text"].strip(),
                    item["page"]
                )
                for item in outline
            ]

    except Exception as e:
        logging.error(f"❌ Failed to open or read {input_path}: {e}")
        return []

    chunks = []

    for i, section in enumerate(outline):
        level = f"H{section[0]}"
        title = section[1].strip()
        page_num = section[2] - 1  

        next_title = None
        next_page = None
        if i + 1 < len(outline):
            next_title = outline[i + 1][1].strip()
            next_page = outline[i + 1][2] - 1

        try:
            if next_title and next_page == page_num:
                text = doc[page_num].get_text()
                if title in text and next_title in text:
                    split = text.split(title, 1)[-1].split(next_title, 1)[0]
                elif title in text:
                    split = text.split(title, 1)[-1]
                else:
                    split = ""

            elif next_page is not None and next_page > page_num:
                content_parts = []
                text = doc[page_num].get_text()
                content_parts.append(text.split(title, 1)[-1] if title in text else text)
                for p in range(page_num + 1, next_page):
                    content_parts.append(doc[p].get_text())
                last_page_text = doc[next_page].get_text()
                if next_title and next_title in last_page_text:
                    content_parts.append(last_page_text.split(next_title, 1)[0])
                else:
                    content_parts.append(last_page_text)
                split = "\n".join(content_parts)

            else:
                text = doc[page_num].get_text()
                split = text.split(title, 1)[-1] if title in text else text

            chunks.append({
                "document": os.path.basename(input_path),
                "level": level,
                "section_title": title,
                "page": section[2],
                "content": split.strip()
            })

        except Exception as e:
            logging.warning(f"⚠️ Failed to process section '{title}' on page {page_num + 1}: {e}")

    return chunks
