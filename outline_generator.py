import pdfplumber
import re
from collections import defaultdict, Counter
def is_heading(line, prev_line, next_line):
    """
    Enhanced heading detection with better bullet point handling
    """
    line = line.strip()
    if not line:
        return None

    numbered_match = re.match(r'^(\d+(\.\d+)*)\s+([A-Z].*)', line)
    if numbered_match:
        level = "H2" if '.' in numbered_match.group(1) else "H1"
        return {"level": level, "text": line}


    if line.isupper() and 1 <= len(line.split()) <= 8:
        return {"level": "H1", "text": line}

    bullet_match = re.match(r'^[-•*]\s*(.*?)(?:\s*[-•*])?$', line)
    if bullet_match:
        bullet_text = bullet_match.group(1).strip()
        if bullet_text and bullet_text[0].isupper():  
            return {"level": "H2", "text": bullet_text}


    words = line.split()
    if (len(words) <= 6 and 
        line[0].isupper() and 
        not line.endswith(('.', '?', '!', ':', ';')) and
        sum(1 for word in words if word[0].isupper()) / len(words) > 0.6):
        return {"level": "H2", "text": line}

    common_headers = {
        "introduction": "H1",
        "abstract": "H1",
        "references": "H1",
        "acknowledgements": "H1",
        "table of contents": "H1",
        "appendix": "H1",
        "conclusion": "H1"
    }
    lower_line = line.lower()
    for header, level in common_headers.items():
        if header in lower_line:
            return {"level": level, "text": line}


    if prev_line or next_line:

        if prev_line and prev_line.endswith(':') and line and line[0].islower():
            return None
        

        if next_line and (not next_line.strip() or next_line.strip()[0] in ('•', '-', '*')):
            if line and line[0].isupper():  # Only if starts with capital
                return {"level": "H2", "text": line}
    
    return None

def extract_headings(pdf_path):
    document = {
        "title": "",
        "outline": []
    }
    
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        first_text = first_page.extract_text()
        if first_text:
            document["title"] = first_text.split('\n')[0].strip()

        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue
                
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            

            potential_headings = []
            for i in range(len(lines)):
                prev_line = lines[i-1] if i > 0 else None
                next_line = lines[i+1] if i < len(lines)-1 else None
                heading = is_heading(lines[i], prev_line, next_line)
                if heading:
                    potential_headings.append((i, heading))
   
            merged_headings = []
            skip_indices = set()
            
            for i, heading in potential_headings:
                if i in skip_indices:
                    continue
                
                current_text = heading["text"]
                current_level = heading["level"]
                j = i + 1
                
                while j < len(lines):
                    next_line = lines[j]
                    if (next_line and next_line[0].islower() and 
                        len(current_text.split()) + len(next_line.split()) < 15 and
                        j not in [x[0] for x in potential_headings]):
                        current_text += " " + next_line
                        skip_indices.add(j)
                        j += 1
                    else:
                        break
                
                merged_headings.append({
                    "level": current_level,
                    "text": current_text,
                    "page": page_num
                })
            
            document["outline"].extend(merged_headings)
    
    seen = set()
    final_outline = []
    
    for heading in document["outline"]:
        key = (heading["text"], heading["page"])
        if key not in seen:
            final_outline.append(heading)
            seen.add(key)
    
    document["outline"] = final_outline
    return document