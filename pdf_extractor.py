# --- pdf_extractor.py ---
import os
import re
import pdfplumber
from typing import List, Dict

MIN_SECTION_LENGTH = 50
MAX_SECTION_LENGTH = 1000

def is_heading(text: str, font_props: dict) -> bool:
    if font_props.get('size', 0) >= 12 or 'bold' in font_props.get('fontname', '').lower():
        return True
    if (text.isupper() or 
        text.endswith(':') or 
        re.match(r'^(Section|Chapter|Part)\s+[IVXLCDM0-9]', text, re.IGNORECASE)):
        return True
    return False

def merge_small_chunks(chunks: List[Dict], min_length: int = MIN_SECTION_LENGTH) -> List[Dict]:
    merged = []
    buffer = None
    for chunk in chunks:
        if len(chunk['content']) < min_length:
            if buffer is None:
                buffer = chunk.copy()
            else:
                buffer['content'] += " " + chunk['content']
                buffer['page'] = max(buffer['page'], chunk['page'])
        else:
            if buffer is not None:
                if len(buffer['content']) >= min_length:
                    merged.append(buffer)
                buffer = None
            merged.append(chunk)
    if buffer is not None and len(buffer['content']) >= min_length:
        merged.append(buffer)
    return merged

def extract_chunks(pdf_path: str) -> List[Dict]:
    chunks = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                words = page.extract_words(extra_attrs=["fontname", "size", "top"])
                text = page.extract_text()
                if not words or not text:
                    continue
                heading_candidates = {}
                current_line = []
                current_line_top = None
                current_font = None
                for word in words:
                    if current_line_top is None or abs(word['top'] - current_line_top) < 5:
                        if current_line_top is None:
                            current_line_top = word['top']
                        current_line.append(word['text'])
                        current_font = {
                            'size': word.get('size', 0),
                            'fontname': word.get('fontname', '').lower()
                        }
                    else:
                        line_text = ' '.join(current_line)
                        if is_heading(line_text, current_font):
                            heading_candidates[current_line_top] = line_text
                        current_line = [word['text']]
                        current_line_top = word['top']
                        current_font = {
                            'size': word.get('size', 0),
                            'fontname': word.get('fontname', '').lower()
                        }
                if current_line:
                    line_text = ' '.join(current_line)
                    if is_heading(line_text, current_font):
                        heading_candidates[current_line_top] = line_text
                sorted_headings = sorted(heading_candidates.items(), key=lambda x: x[0])
                headings = [h[1] for h in sorted_headings]
                paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                current_heading = "Introduction"
                heading_idx = 0
                for para in paragraphs:
                    first_line = para.split('\n')[0].strip()
                    if (is_heading(first_line, {'size': 0, 'fontname': ''}) or
                        (heading_idx < len(headings) and first_line == headings[heading_idx])):
                        current_heading = headings[heading_idx]
                        heading_idx += 1
                        content = '\n'.join(para.split('\n')[1:]).strip()
                    else:
                        content = para
                    if content and len(content) > 20:
                        chunks.append({
                            "document": os.path.basename(pdf_path),
                            "section_title": current_heading[:200],
                            "content": content[:MAX_SECTION_LENGTH],
                            "page": page_num
                        })
        chunks = merge_small_chunks(chunks)
        print(f"\u2705 {os.path.basename(pdf_path)}: {len(chunks)} chunks extracted.")
        return chunks
    except Exception as e:
        print(f"\u274C Error processing {pdf_path}: {str(e)}")
        return []