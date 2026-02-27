"""
RAG Service — FAISS-based knowledge retrieval engine.

Architecture:
  1. At startup, load all .txt/.json docs from data/docs/
  2. Chunk them, embed with a lightweight local model (sentence-transformers)
  3. Build/load a FAISS index on disk → works OFFLINE
  4. At query time: embed the question → search FAISS → return top-k chunks
  5. These chunks are injected into the IBM watsonx prompt as context

This means:
  - Knowledge retrieval works OFFLINE (FAISS + local embeddings)
  - AI generation uses IBM watsonx when online, falls back gracefully
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ── Paths ─────────────────────────────────────────────────────────────────────

BASE_DIR        = Path(__file__).resolve().parents[2]
DOCS_DIR        = BASE_DIR / "data" / "docs"
INDEX_PATH      = BASE_DIR / "data" / "faiss.index"
CHUNKS_PATH     = BASE_DIR / "data" / "chunks.pkl"

# ── Config ────────────────────────────────────────────────────────────────────

EMBED_MODEL     = "all-MiniLM-L6-v2"   # ~80 MB, runs fully offline after first download
CHUNK_SIZE      = 400                   # characters per chunk
CHUNK_OVERLAP   = 80
TOP_K           = 4                     # how many chunks to retrieve per query

# ── Globals (loaded once at startup) ─────────────────────────────────────────

_embedder: SentenceTransformer = None
_index: faiss.Index             = None
_chunks: List[dict]             = []    # [{"text": ..., "source": ..., "lang": ...}]


def _load_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        print(f"[RAG] Loading embedding model: {EMBED_MODEL}")
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


def _chunk_text(text: str, source: str, lang: str = "en") -> List[dict]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()
        if len(chunk) > 50:  # skip tiny fragments
            chunks.append({"text": chunk, "source": source, "lang": lang})
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def _load_docs() -> List[dict]:
    """Load all documents from data/docs/. Supports .txt and .json."""
    all_chunks = []
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    for doc_path in DOCS_DIR.glob("**/*"):
        if doc_path.suffix == ".txt":
            text = doc_path.read_text(encoding="utf-8", errors="ignore")
            lang = doc_path.stem.split("_")[-1] if "_" in doc_path.stem else "en"
            all_chunks.extend(_chunk_text(text, source=doc_path.name, lang=lang))

        elif doc_path.suffix == ".json":
            data = json.loads(doc_path.read_text(encoding="utf-8"))
            # Expected format: [{"text": "...", "lang": "en", "topic": "..."}]
            if isinstance(data, list):
                for item in data:
                    text = item.get("text", "")
                    lang = item.get("lang", "en")
                    src  = item.get("topic", doc_path.name)
                    all_chunks.extend(_chunk_text(text, source=src, lang=lang))

    print(f"[RAG] Loaded {len(all_chunks)} chunks from {DOCS_DIR}")
    return all_chunks


def build_index(force: bool = False):
    """
    Build (or load cached) FAISS index.
    Call this at app startup via a lifespan event or manually.
    Set force=True to rebuild from scratch.
    """
    global _index, _chunks

    if not force and INDEX_PATH.exists() and CHUNKS_PATH.exists():
        print("[RAG] Loading cached FAISS index...")
        _index  = faiss.read_index(str(INDEX_PATH))
        with open(CHUNKS_PATH, "rb") as f:
            _chunks = pickle.load(f)
        print(f"[RAG] Index loaded — {_index.ntotal} vectors, {len(_chunks)} chunks")
        return

    print("[RAG] Building FAISS index from documents...")
    embedder = _load_embedder()
    _chunks  = _load_docs()

    if not _chunks:
        # Seed with built-in fallback knowledge so demo works out-of-the-box
        _chunks = _get_seed_knowledge()

    texts      = [c["text"] for c in _chunks]
    embeddings = embedder.encode(texts, show_progress_bar=True, batch_size=64)
    embeddings = np.array(embeddings, dtype="float32")

    dim    = embeddings.shape[1]
    _index = faiss.IndexFlatL2(dim)
    _index.add(embeddings)

    # Persist to disk (offline reuse)
    faiss.write_index(_index, str(INDEX_PATH))
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(_chunks, f)

    print(f"[RAG] Index built — {_index.ntotal} vectors saved to {INDEX_PATH}")


def retrieve(query: str, top_k: int = TOP_K) -> List[Tuple[str, str, float]]:
    """
    Search FAISS for the most relevant knowledge chunks.

    Returns:
        List of (chunk_text, source_name, distance_score)
    """
    global _index, _chunks

    if _index is None or not _chunks:
        build_index()

    embedder = _load_embedder()
    q_vec    = embedder.encode([query], convert_to_numpy=True).astype("float32")

    distances, indices = _index.search(q_vec, top_k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < len(_chunks):
            chunk = _chunks[idx]
            results.append((chunk["text"], chunk["source"], float(dist)))

    return results


def format_context(results: List[Tuple[str, str, float]]) -> str:
    """Format retrieved chunks into a clean context string for the LLM prompt."""
    if not results:
        return "No specific knowledge found. Use general agricultural expertise."

    parts = ["=== RETRIEVED KNOWLEDGE ==="]
    for i, (text, source, score) in enumerate(results, 1):
        parts.append(f"[{i}] (Source: {source})\n{text}")
    parts.append("=== END OF KNOWLEDGE ===")
    return "\n\n".join(parts)


def get_index_stats() -> dict:
    """Return stats about the loaded index — used by /health endpoint."""
    return {
        "vectors": _index.ntotal if _index else 0,
        "chunks":  len(_chunks),
        "index_file_exists": INDEX_PATH.exists(),
    }


# ── Seed knowledge (built-in fallback so demo works without any docs) ─────────

def _get_seed_knowledge() -> List[dict]:
    """
    Minimal built-in agricultural knowledge so the system works
    out-of-the-box during a hackathon demo even without external docs.
    """
    entries = [
        # Crops
        ("Wheat (Triticum aestivum) is a major rabi crop in India. Sowing season: October–December. "
         "Harvest: March–April. Requires well-drained loamy soil. Major states: Punjab, Haryana, UP. "
         "Common varieties: HD-2967, PBW-343, DBW-187.", "wheat_basics"),

        ("Rice (Paddy) is the most important kharif crop in India. Transplanting: June–July. "
         "Harvest: October–November. Requires flooded fields and warm humid climate. "
         "Major varieties: Swarna, MTU-7029, Pusa Basmati 1121.", "rice_basics"),

        ("Cotton is a kharif crop grown in black soil. Sowing: May–June. "
         "Harvest: October–February. Requires 6–8 months warm weather. "
         "Bt Cotton is widely used in India to resist bollworm.", "cotton_basics"),

        ("Tomato can be grown year-round. Transplant 25-day-old seedlings. Spacing: 60x45 cm. "
         "Requires staking. Common diseases: early blight, late blight, leaf curl virus. "
         "Fertilizer: NPK 120:60:60 kg/ha.", "tomato_basics"),

        # Fertilizers
        ("Nitrogen (N) promotes leafy green growth. Sources: Urea (46% N), DAP (18% N). "
         "Apply urea in splits — at sowing and at tillering stage. "
         "Excess nitrogen causes lodging and attracts pests.", "fertilizer_nitrogen"),

        ("Phosphorus (P) promotes root development and flowering. Source: DAP, SSP. "
         "Apply at sowing time as basal dose. SSP also provides Sulphur.", "fertilizer_phosphorus"),

        ("Potassium (K) improves disease resistance and fruit quality. Source: MOP (Muriate of Potash). "
         "Apply at flowering and fruiting stage.", "fertilizer_potassium"),

        # Pests & Diseases
        ("Rice blast (Magnaporthe oryzae): Grey-green lesions with brown margins on leaves. "
         "Control: Spray Tricyclazole 75 WP @ 0.6 g/L or Carbendazim 50 WP @ 1 g/L.", "rice_blast"),

        ("Late blight in tomato/potato (Phytophthora infestans): Water-soaked spots on leaves, "
         "white fungal growth on underside. Spreads in cool humid weather. "
         "Control: Mancozeb 75 WP @ 2.5 g/L or Metalaxyl+Mancozeb.", "late_blight"),

        ("Aphids suck sap from new growth causing curling leaves and stunting. "
         "Control: Imidacloprid 17.8 SL @ 0.5 ml/L or neem oil spray @ 5 ml/L.", "aphids"),

        ("Stem borer in rice: Dead heart in vegetative stage, white ear head at maturity. "
         "Control: Cartap Hydrochloride 4G @ 18 kg/ha or release Trichogramma cards.", "stem_borer"),

        # Irrigation
        ("Drip irrigation saves 40–60% water compared to flood irrigation. "
         "Best for vegetables, fruits, sugarcane. Government subsidy available under PMKSY.", "drip_irrigation"),

        ("Critical irrigation stages for wheat: Crown root initiation (21 DAS), tillering (45 DAS), "
         "jointing (65 DAS), flowering (85 DAS), grain filling (105 DAS). "
         "Total water requirement: 35–40 cm.", "wheat_irrigation"),

        # Government Schemes
        ("PM-KISAN (Pradhan Mantri Kisan Samman Nidhi): Direct income support of Rs 6,000/year "
         "in 3 installments of Rs 2,000 to small and marginal farmers owning up to 2 hectares. "
         "Register at pmkisan.gov.in or nearest CSC.", "pm_kisan"),

        ("PM Fasal Bima Yojana (PMFBY): Crop insurance scheme. Premium: 2% for kharif, "
         "1.5% for rabi, 5% for commercial crops. Covers yield loss due to natural calamities, "
         "pests, diseases. Enroll through bank or insurance company before cutoff date.", "pmfby"),

        ("Soil Health Card Scheme: Free soil testing by government. Card shows NPK status, "
         "pH, micronutrients. Helps farmers apply correct fertilizer dose. "
         "Apply at nearest Krishi Vigyan Kendra (KVK).", "soil_health_card"),

        ("Kisan Credit Card (KCC): Short-term credit for crop production, post-harvest expenses, "
         "and allied activities. Loan up to Rs 3 lakh at 4% interest after subvention. "
         "Apply at any nationalized bank or cooperative bank.", "kisan_credit_card"),

        # Soil
        ("Soil pH: Ideal for most crops is 6.0–7.5. Below 6 (acidic) — apply lime. "
         "Above 7.5 (alkaline) — apply gypsum or sulphur. Test soil every 3 years.", "soil_ph"),

        ("Organic matter in soil improves water retention and nutrient availability. "
         "Add FYM (Farm Yard Manure) 10–15 tonnes/ha. Vermicompost 4–5 tonnes/ha. "
         "Green manuring with Dhaincha or Sunhemp before transplanting.", "soil_organic"),

        # Hindi entries
        ("गेहूं की बुवाई का सही समय अक्टूबर से दिसंबर है। बुवाई से पहले बीज उपचार करें। "
         "यूरिया की पहली मात्रा बुवाई के समय और दूसरी मात्रा पहली सिंचाई के बाद डालें। "
         "HD-2967 और DBW-187 अच्छी किस्में हैं।", "wheat_hi"),

        ("धान में भूरा माहो (Brown Plant Hopper) एक गंभीर कीट है। "
         "नियंत्रण: Imidacloprid 17.8 SL 0.5 ml प्रति लीटर पानी में मिलाकर छिड़काव करें। "
         "खेत में पानी निकाल दें और रोशनी जाल का उपयोग करें।", "bph_hi"),

        ("पीएम किसान योजना के तहत किसानों को हर साल 6000 रुपये मिलते हैं। "
         "यह राशि तीन किस्तों में सीधे बैंक खाते में आती है। "
         "pmkisan.gov.in पर या नजदीकी CSC केंद्र पर पंजीकरण करें।", "pmkisan_hi"),

        # Telugu entries
        ("వరి పంటలో దోమపోటు (BPH) తెగులు నివారణకు Imidacloprid 17.8 SL "
         "0.5 మి.లీ. ఒక లీటరు నీటికి కలిపి పిచికారీ చేయాలి. "
         "పొలంలో నీరు తీసివేసి వెలుతురు ఉచ్చులు వాడాలి.", "bph_te"),

        ("PM-KISAN పథకం కింద రైతులకు సంవత్సరానికి 6000 రూపాయలు "
         "మూడు వాయిదాల్లో నేరుగా బ్యాంకు ఖాతాకు జమ అవుతాయి.", "pmkisan_te"),
    ]

    chunks = []
    for text, source in entries:
        lang = source.split("_")[-1] if source.split("_")[-1] in ["hi", "te", "ta", "mr"] else "en"
        chunks.extend(_chunk_text(text, source=source, lang=lang))
    return chunks
