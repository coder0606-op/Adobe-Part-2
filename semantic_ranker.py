import numpy as np
import onnxruntime as ort
from datetime import datetime
from typing import List, Dict
from transformers import AutoTokenizer

print("✅ semantic_ranker.py: using ONNX model via onnxruntime")

tokenizer = AutoTokenizer.from_pretrained("./")
onnx_session = ort.InferenceSession("./model.onnx")

def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def encode(texts: List[str]) -> np.ndarray:
    """Encode a list of texts into embeddings using ONNX model."""
    encoded_inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        return_tensors="np",
        return_token_type_ids=True  
    )

    ort_inputs = {
        "input_ids": encoded_inputs["input_ids"],
        "attention_mask": encoded_inputs["attention_mask"],
        "token_type_ids": encoded_inputs["token_type_ids"],
    }

    outputs = onnx_session.run(None, ort_inputs)
    last_hidden_state = outputs[0] 


    input_mask_expanded = np.expand_dims(encoded_inputs["attention_mask"], -1)
    sum_embeddings = np.sum(last_hidden_state * input_mask_expanded, axis=1)
    sum_mask = np.clip(input_mask_expanded.sum(1), a_min=1e-9, a_max=None)
    return sum_embeddings / sum_mask



def rank_chunks_by_relevance(
    chunks: List[Dict],
    persona: str,
    job: str,
    top_k: int = 5
) -> List[Dict]:
    """Rank all chunks by semantic similarity and return the top K with metadata."""
    query = f"{persona}. Task: {job}"
    query_embedding = encode([query])[0] 
    
    chunk_texts = [f"{chunk['section_title']} {chunk['content']}" for chunk in chunks]
    chunk_embeddings = encode(chunk_texts)  

    for i, chunk in enumerate(chunks):
        score = cosine_similarity(query_embedding, chunk_embeddings[i])
        chunk["score"] = round(float(score), 4)

    scored_chunks = sorted(chunks, key=lambda x: x["score"], reverse=True)

    for i, chunk in enumerate(scored_chunks[:top_k]):
        chunk["importance_rank"] = i + 1

    return scored_chunks[:top_k]


def format_output(
    input_docs: List[str],
    persona: str,
    job: str,
    top_chunks: List[Dict]
) -> Dict:
    timestamp = get_current_timestamp()
    output = {
        "metadata": {
            "input_documents": input_docs,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": timestamp,
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
            "section_title": chunk["section_title"],
            "refined_text": chunk["content"],
            "page_number": chunk["page"]
        })

    return output
