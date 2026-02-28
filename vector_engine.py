"""
FAISS Vector Search Engine for FarmAI
Builds and queries semantic search index over the knowledge base.
"""

import os
import json
import pickle
import numpy as np
from pathlib import Path

CACHE_DIR = Path("model_cache")
INDEX_FILE = CACHE_DIR / "faiss_index.pkl"
META_FILE  = CACHE_DIR / "faiss_meta.pkl"

_index    = None
_metadata = []
_model    = None


def _load_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print("[FarmAI] Loading embedding model …")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[FarmAI] Model loaded.")
    return _model


def build_index(force_rebuild: bool = False):
    """Build (or load cached) FAISS index from the knowledge base."""
    global _index, _metadata

    CACHE_DIR.mkdir(exist_ok=True)

    if not force_rebuild and INDEX_FILE.exists() and META_FILE.exists():
        print("[FarmAI] Loading FAISS index from cache …")
        with open(INDEX_FILE, "rb") as f:
            _index = pickle.load(f)
        with open(META_FILE, "rb") as f:
            _metadata = pickle.load(f)
        print(f"[FarmAI] Loaded {len(_metadata)} documents from cache.")
        return

    from knowledge_base import get_all_documents
    import faiss

    model = _load_model()
    docs  = get_all_documents()

    texts = [text for _, text, _ in docs]
    ids   = [doc_id for doc_id, _, _ in docs]
    metas = [meta for _, _, meta in docs]

    print(f"[FarmAI] Encoding {len(texts)} documents …")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    embeddings = embeddings.astype(np.float32)

    dim   = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)   # inner-product on L2-normalised vecs == cosine
    index.add(embeddings)

    _index    = index
    _metadata = list(zip(ids, metas, texts))

    with open(INDEX_FILE, "wb") as f:
        pickle.dump(_index, f)
    with open(META_FILE, "wb") as f:
        pickle.dump(_metadata, f)

    print(f"[FarmAI] Index built with {index.ntotal} vectors (dim={dim}).")


def semantic_search(query: str, top_k: int = 5, category_filter: str = None):
    """
    Search the knowledge base for the most relevant documents.

    Returns list of dicts with keys: id, title, category, content, score.
    """
    global _index, _metadata

    if _index is None:
        build_index()

    model = _load_model()
    q_emb = model.encode([query], normalize_embeddings=True).astype(np.float32)
    scores, indices = _index.search(q_emb, top_k * 3)   # fetch extra for filtering

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(_metadata):
            continue
        doc_id, meta, _ = _metadata[idx]
        if category_filter and meta["category"] != category_filter:
            continue
        results.append({
            "id":       doc_id,
            "title":    meta["title"],
            "category": meta["category"],
            "content":  meta["content"],
            "score":    float(score),
        })
        if len(results) >= top_k:
            break

    return results


def get_answer(query: str, top_k: int = 3, category_filter: str = None) -> dict:
    """
    Generate a structured answer from the knowledge base.
    Returns the top results and a synthesised answer paragraph.
    """
    results = semantic_search(query, top_k=top_k, category_filter=category_filter)

    if not results:
        return {
            "answer": (
                "I'm sorry, I don't have specific information about that topic in my "
                "knowledge base. Please consult your local Krishi Vigyan Kendra (KVK) "
                "or call the Kisan Call Centre at 1800-180-1551 (toll-free)."
            ),
            "sources": [],
            "confidence": 0.0,
        }

    top = results[0]
    confidence = top["score"]

    if confidence < 0.25:
        answer = (
            f"Based on related information: {top['content'][:400]}… "
            f"For more specific advice, contact Kisan Call Centre: 1800-180-1551."
        )
    else:
        # Compose a rich answer from the top result + supporting details
        supporting = ""
        if len(results) > 1:
            extra_titles = [r["title"] for r in results[1:3]]
            supporting = f" Related topics: {', '.join(extra_titles)}."

        answer = (
            f"**{top['title']}**\n\n"
            f"{top['content']}"
            f"{supporting}"
        )

    return {
        "answer":     answer,
        "sources":    results,
        "confidence": round(confidence, 3),
    }
