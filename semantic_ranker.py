import numpy as np
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
import onnxruntime as ort
from transformers import AutoTokenizer

MAX_TOKENS = 256
TOKENIZER_PATH = "tokenizer"
MODEL_PATH = "model.onnx"

def initialize_models():
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
    options = ort.SessionOptions()
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    options.intra_op_num_threads = 4
    session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'], sess_options=options)
    return tokenizer, session

def compute_onnx_embeddings(texts: List[str], session, tokenizer) -> np.ndarray:
    inputs = tokenizer(texts, padding=True, truncation=True, max_length=MAX_TOKENS, return_tensors="np")
    ort_inputs = {
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs["attention_mask"],
        "token_type_ids": np.zeros_like(inputs["input_ids"])
    }
    token_embeddings = session.run(None, ort_inputs)[0]
    input_mask_expanded = np.expand_dims(inputs["attention_mask"], -1)
    embeddings = np.sum(token_embeddings * input_mask_expanded, axis=1) / np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings

def hybrid_scoring(chunks: List[Dict], job: str, tokenizer, session) -> List[Dict]:
    if not chunks:
        return chunks
    chunk_texts = [chunk['content'] for chunk in chunks]
    all_texts = [job] + chunk_texts
    embeddings = compute_onnx_embeddings(all_texts, session, tokenizer)
    job_embedding = embeddings[0]
    chunk_embeddings = embeddings[1:]
    semantic_scores = np.dot(chunk_embeddings, job_embedding)
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = vectorizer.fit_transform([job] + chunk_texts)
    job_tfidf = tfidf_matrix[0]
    chunk_tfidfs = tfidf_matrix[1:]
    keyword_scores = np.asarray(chunk_tfidfs.dot(job_tfidf.T).toarray().flatten())
    semantic_scores = (semantic_scores - semantic_scores.min()) / (semantic_scores.max() - semantic_scores.min() + 1e-9)
    keyword_scores = (keyword_scores - keyword_scores.min()) / (keyword_scores.max() - keyword_scores.min() + 1e-9)
    for i, chunk in enumerate(chunks):
        chunk['semantic_score'] = float(semantic_scores[i])
        chunk['keyword_score'] = float(keyword_scores[i])
        chunk['score'] = 0.7 * semantic_scores[i] + 0.3 * keyword_scores[i]
    return chunks

def rank_chunks(chunks: List[Dict], job: str) -> List[Dict]:
    if not chunks:
        print("No chunks available for ranking")
        return []
    try:
        global tokenizer, session
        if 'tokenizer' not in globals() or 'session' not in globals():
            tokenizer, session = initialize_models()
        scored_chunks = hybrid_scoring(chunks, job, tokenizer, session)
        ranked_chunks = sorted(scored_chunks, key=lambda x: x['score'], reverse=True)[:5]
        for i, chunk in enumerate(ranked_chunks):
            chunk['importance_rank'] = i + 1
        print(f"Ranked {len(chunks)} chunks, selected top {len(ranked_chunks)}")
        return ranked_chunks
    except Exception as e:
        print(f"Error in ranking chunks: {str(e)}")
        return []