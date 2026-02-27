"""
=============================================================================
FarmAI — Crop Assistant API (Single-File Version)
=============================================================================
AI-powered assistant for farmers using FAISS knowledge retrieval + IBM watsonx.
Features: crop Q&A, disease diagnosis, weather advice, government schemes,
          multilingual, offline-capable.

This is a merged single-file version of the entire FarmAI project.
All Python modules (main, routers, services) are combined here.
Non-Python files (requirements.txt, .env.example, sample_knowledge.json,
README.md) are embedded at the bottom as string constants.
=============================================================================
"""

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS (deduplicated from all modules)
# ═══════════════════════════════════════════════════════════════════════════════

import os
import sys
import json
import pickle
from pathlib import Path
from typing import Optional, List, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field

# IBM SDK — install with: pip install ibm-watsonx-ai
try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    IBM_AVAILABLE = True
except ImportError:
    IBM_AVAILABLE = False
    print("[IBM] ibm-watsonx-ai not installed. Run: pip install ibm-watsonx-ai")


# ═══════════════════════════════════════════════════════════════════════════════
# IBM SERVICE (from ibm_service.py)
# ═══════════════════════════════════════════════════════════════════════════════

# ── Config (set in .env) ──────────────────────────────────────────────────────

IBM_API_KEY    = os.getenv("IBM_API_KEY", "")
IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID", "")
IBM_URL        = os.getenv("IBM_URL", "https://us-south.ml.cloud.ibm.com")

# Model options (choose based on your watsonx plan):
#   "ibm/granite-13b-instruct-v2"      — IBM's own model, fast, good for instructions
#   "meta-llama/llama-3-70b-instruct"  — Llama 3 70B, best quality
#   "mistralai/mistral-large"          — Mistral, good multilingual
IBM_MODEL_ID   = os.getenv("IBM_MODEL_ID", "ibm/granite-13b-instruct-v2")

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "mr": "Marathi",
    "kn": "Kannada",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "bn": "Bengali",
}

FARM_SYSTEM_PROMPT = """You are FarmAI, a trusted agricultural assistant for Indian farmers.
You have deep knowledge of crops, pests, fertilizers, irrigation, soil, and government schemes.

Rules:
- Give practical, actionable advice farmers can use immediately.
- Use simple language — avoid technical jargon unless needed.
- Always respond in the language requested.
- If the retrieved knowledge contains the answer, use it. If not, use your general expertise.
- Mention government schemes (PM-KISAN, PMFBY, KCC, etc.) when relevant.
- If unsure, say so and recommend consulting a local Krishi Vigyan Kendra (KVK).
"""


def ask_watsonx(
    user_message: str,
    context: str = "",
    language: str = "en",
    conversation_history: Optional[list] = None,
    extra_instructions: str = "",
) -> dict:
    """
    Send a message to IBM watsonx and get a farming response.

    Args:
        user_message:          Farmer's question
        context:               Retrieved FAISS knowledge chunks
        language:              Language code (en, hi, te, ...)
        conversation_history:  Previous turns [{"role": ..., "content": ...}]
        extra_instructions:    Extra system prompt additions (used by sub-routers)

    Returns:
        dict with keys: answer (str), source (str), language_used (str)
    """
    lang_name = SUPPORTED_LANGUAGES.get(language, "English")

    # Build the full prompt
    system = FARM_SYSTEM_PROMPT
    system += f"\n\nIMPORTANT: Always respond in {lang_name}."
    if extra_instructions:
        system += f"\n\n{extra_instructions.strip()}"

    # Build conversation
    history_text = ""
    if conversation_history:
        for turn in conversation_history:
            role = "Farmer" if turn["role"] == "user" else "FarmAI"
            history_text += f"{role}: {turn['content']}\n"

    prompt = _build_prompt(
        system=system,
        context=context,
        history=history_text,
        question=user_message,
    )

    # Try IBM watsonx first
    if IBM_AVAILABLE and IBM_API_KEY:
        try:
            answer = _call_watsonx(prompt)
            return {"answer": answer, "source": "ibm_watsonx", "language_used": lang_name}
        except Exception as e:
            print(f"[IBM] watsonx call failed: {e} — falling back to offline mode")

    # Offline fallback — returns context directly with a helpful wrapper
    answer = _offline_fallback(user_message, context, lang_name)
    return {"answer": answer, "source": "offline_rag", "language_used": lang_name}


def _build_prompt(system: str, context: str, history: str, question: str) -> str:
    """Construct the full prompt string for watsonx."""
    parts = [system]

    if context and "No specific knowledge" not in context:
        parts.append(f"\n{context}")

    if history:
        parts.append(f"\nConversation so far:\n{history}")

    parts.append(f"\nFarmer's question: {question}")
    parts.append("\nFarmAI's response:")
    return "\n".join(parts)


def _call_watsonx(prompt: str) -> str:
    """Call IBM watsonx.ai API and return the generated text."""
    credentials = Credentials(url=IBM_URL, api_key=IBM_API_KEY)
    client      = APIClient(credentials=credentials, project_id=IBM_PROJECT_ID)

    model = ModelInference(
        model_id=IBM_MODEL_ID,
        api_client=client,
        params={
            GenParams.MAX_NEW_TOKENS:  800,
            GenParams.MIN_NEW_TOKENS:  30,
            GenParams.TEMPERATURE:     0.4,
            GenParams.TOP_P:           0.9,
            GenParams.REPETITION_PENALTY: 1.1,
        },
    )

    response = model.generate_text(prompt=prompt)
    return response.strip()


def _offline_fallback(question: str, context: str, lang_name: str) -> str:
    """
    Offline fallback — returns retrieved knowledge with a structured wrapper.
    Used when IBM watsonx is unreachable (low connectivity scenario).
    """
    if not context or "No specific knowledge" in context:
        return (
            f"[OFFLINE MODE — {lang_name}]\n"
            "I couldn't find specific information for your question in the local knowledge base. "
            "Please visit your nearest Krishi Vigyan Kendra (KVK) or call the Kisan Call Centre: 1800-180-1551 (free)."
        )

    return (
        f"[OFFLINE MODE — {lang_name}]\n"
        "Based on local agricultural knowledge:\n\n"
        + "\n\n".join(
            chunk.strip()
            for chunk in context.replace("=== RETRIEVED KNOWLEDGE ===", "")
                                 .replace("=== END OF KNOWLEDGE ===", "")
                                 .split("\n\n")
            if chunk.strip() and not chunk.startswith("[")
        )
        + "\n\n📞 For more help: Kisan Call Centre 1800-180-1551 (free, 24x7)"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# RAG SERVICE (from rag_service.py)
# ═══════════════════════════════════════════════════════════════════════════════

# ── Paths ─────────────────────────────────────────────────────────────────────

BASE_DIR        = Path(__file__).resolve().parent
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


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTERS — CHAT (from chat.py)
# ═══════════════════════════════════════════════════════════════════════════════

chat_router = APIRouter()


class Message(BaseModel):
    role: str     = Field(..., description="'user' or 'assistant'")
    content: str


class ChatRequest(BaseModel):
    message:  str            = Field(..., description="Farmer's question")
    language: str            = Field(default="en", description="Language code: en, hi, te, ta, mr, kn, gu, pa, bn")
    history:  Optional[list[Message]] = Field(default=None, description="Previous conversation turns")


class ChatResponse(BaseModel):
    reply:         str
    sources:       list[str]
    language_used: str
    mode:          str  # "ibm_watsonx" or "offline_rag"


@chat_router.post("/", response_model=ChatResponse, summary="Ask FarmAI any crop question")
def chat(req: ChatRequest):
    """
    Ask any farming question — crop care, pests, fertilizers, irrigation, etc.
    
    - FAISS searches the local knowledge base first
    - Retrieved knowledge is injected into the IBM watsonx prompt
    - Works offline (returns raw knowledge if IBM is unreachable)
    - Multilingual: set `language` to en/hi/te/ta/mr/kn/gu/pa/bn
    """
    # Step 1: Retrieve relevant knowledge from FAISS
    results = retrieve(req.message)
    context = format_context(results)
    sources = list({src for _, src, _ in results})

    # Step 2: Generate answer with IBM watsonx
    history = [{"role": m.role, "content": m.content} for m in req.history] if req.history else []
    result  = ask_watsonx(
        user_message=req.message,
        context=context,
        language=req.language,
        conversation_history=history,
    )

    return ChatResponse(
        reply=result["answer"],
        sources=sources,
        language_used=result["language_used"],
        mode=result["source"],
    )


@chat_router.get("/languages", summary="List supported languages")
def get_languages():
    return {"supported_languages": SUPPORTED_LANGUAGES}


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTERS — DISEASE (from disease.py)
# ═══════════════════════════════════════════════════════════════════════════════

disease_router = APIRouter()

DISEASE_INSTRUCTIONS = """
You are diagnosing a crop disease. Structure your response as:

1. TOP SUSPECTED DISEASES (list 2-3 with confidence level)
2. FOR EACH DISEASE:
   - Symptoms match: explain what matched
   - Immediate treatment: specific chemicals/doses or organic remedies
   - Spread risk: can it spread? How to contain?
3. PREVENTION for next season
4. When to call an expert

Be specific with chemical names and dosages. Mention generic/cheap alternatives.
"""


class DiagnosisRequest(BaseModel):
    crop:            str           = Field(..., description="Crop name (e.g., 'wheat', 'tomato', 'rice')")
    symptoms:        str           = Field(..., description="What you observe: leaf color, spots, wilting, smell, etc.")
    language:        str           = Field(default="en")
    growth_stage:    Optional[str] = Field(default=None, description="seedling / vegetative / flowering / fruiting / harvest")
    additional_info: Optional[str] = Field(default=None, description="Recent weather, soil type, crop age, nearby crops")


class DiagnosisResponse(BaseModel):
    crop:          str
    diagnosis:     str
    sources:       list[str]
    language_used: str
    mode:          str


@disease_router.post("/", response_model=DiagnosisResponse, summary="Diagnose disease from symptoms")
def diagnose(req: DiagnosisRequest):
    """
    Describe what you see on your crop and get AI-powered disease diagnosis
    with treatment recommendations and chemical dosages.

    **Better inputs → better diagnosis:**
    - Which part of plant is affected? (leaf, stem, root, fruit)
    - Color changes, spots, smell, texture
    - When did it start? Is it spreading?
    - Recent weather (rain, humidity, drought)
    """
    # Build a rich search query combining crop + symptoms
    search_query = f"{req.crop} disease {req.symptoms}"
    if req.growth_stage:
        search_query += f" {req.growth_stage} stage"

    results = retrieve(search_query)
    context = format_context(results)
    sources = list({src for _, src, _ in results})

    # Build the full message for IBM watsonx
    parts = [f"Crop: {req.crop}"]
    if req.growth_stage:
        parts.append(f"Growth stage: {req.growth_stage}")
    parts.append(f"Symptoms observed: {req.symptoms}")
    if req.additional_info:
        parts.append(f"Additional context: {req.additional_info}")
    parts.append("Please diagnose and give treatment advice.")

    result = ask_watsonx(
        user_message="\n".join(parts),
        context=context,
        language=req.language,
        extra_instructions=DISEASE_INSTRUCTIONS,
    )

    return DiagnosisResponse(
        crop=req.crop,
        diagnosis=result["answer"],
        sources=sources,
        language_used=result["language_used"],
        mode=result["source"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTERS — WEATHER (from weather.py)
# ═══════════════════════════════════════════════════════════════════════════════

weather_router = APIRouter()

WEATHER_INSTRUCTIONS = """
You are a weather-aware farming advisor. Given the weather and crop info:
1. Assess weather impact on the crop at its current stage
2. Give specific advice on irrigation, spraying, harvesting windows
3. Warn about disease risk (high humidity = fungal risk, etc.)
4. If wind > 15 km/h: advise against spraying
5. Give day-by-day recommendations if forecast is provided
Keep advice practical and time-sensitive.
"""


class WeatherData(BaseModel):
    temperature_c:      Optional[float] = None
    humidity_percent:   Optional[float] = None
    rainfall_mm:        Optional[float] = None
    wind_speed_kmh:     Optional[float] = None
    condition:          Optional[str]   = Field(default=None, description="sunny/cloudy/rainy/foggy/stormy")
    forecast_next_days: Optional[str]   = Field(default=None, description="e.g. '3 days of rain expected'")


class WeatherRequest(BaseModel):
    crop:             str              = Field(..., description="Crop name")
    crop_stage:       Optional[str]   = Field(default=None, description="seedling/vegetative/flowering/fruiting/harvest-ready")
    planned_activity: Optional[str]   = Field(default=None, description="What you plan to do today")
    location:         Optional[str]   = Field(default=None, description="State or region")
    weather:          WeatherData
    language:         str             = Field(default="en")


class WeatherResponse(BaseModel):
    crop:          str
    advice:        str
    sources:       list[str]
    language_used: str
    mode:          str


@weather_router.post("/advice", response_model=WeatherResponse, summary="Get weather-based crop advice")
def weather_advice(req: WeatherRequest):
    """
    Get farming advice tailored to current weather conditions.
    Handles irrigation decisions, spray timing, frost/heat alerts, harvest windows.
    """
    w = req.weather
    weather_parts = []
    if w.condition:          weather_parts.append(f"Condition: {w.condition}")
    if w.temperature_c:      weather_parts.append(f"Temp: {w.temperature_c}°C")
    if w.humidity_percent:   weather_parts.append(f"Humidity: {w.humidity_percent}%")
    if w.rainfall_mm:        weather_parts.append(f"Rainfall: {w.rainfall_mm}mm")
    if w.wind_speed_kmh:     weather_parts.append(f"Wind: {w.wind_speed_kmh} km/h")
    if w.forecast_next_days: weather_parts.append(f"Forecast: {w.forecast_next_days}")

    search_query = f"{req.crop} {req.planned_activity or 'farming advice'} weather {w.condition or ''}"
    results = retrieve(search_query)
    context = format_context(results)
    sources = list({src for _, src, _ in results})

    parts = [f"Crop: {req.crop}"]
    if req.crop_stage:       parts.append(f"Stage: {req.crop_stage}")
    if req.location:         parts.append(f"Location: {req.location}")
    if req.planned_activity: parts.append(f"Planned activity: {req.planned_activity}")
    parts.append("Weather: " + " | ".join(weather_parts))
    parts.append("What should I do for my crop today?")

    result = ask_watsonx(
        user_message="\n".join(parts),
        context=context,
        language=req.language,
        extra_instructions=WEATHER_INSTRUCTIONS,
    )

    return WeatherResponse(
        crop=req.crop,
        advice=result["answer"],
        sources=sources,
        language_used=result["language_used"],
        mode=result["source"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTERS — SCHEMES (from schemes.py)
# ═══════════════════════════════════════════════════════════════════════════════

schemes_router = APIRouter()

SCHEMES_INSTRUCTIONS = """
You are an expert on Indian government agricultural schemes and subsidies.
When answering:
1. Name the relevant scheme(s) clearly
2. Explain eligibility in simple terms (who qualifies)
3. Explain the benefit (money, subsidy, loan, insurance, etc.)
4. Explain HOW to apply (website, bank, CSC, documents needed)
5. Mention deadlines if known
6. Mention the helpline number if available
Always be encouraging — many farmers don't know they qualify for these benefits.
"""


class SchemesRequest(BaseModel):
    query:      str           = Field(..., description="What scheme info do you need? Or describe your situation.")
    state:      Optional[str] = Field(default=None, description="State (some schemes are state-specific)")
    farmer_type: Optional[str] = Field(default=None, description="small/marginal/large/tenant/women")
    language:   str           = Field(default="en")


class SchemesResponse(BaseModel):
    answer:        str
    sources:       list[str]
    language_used: str
    mode:          str


@schemes_router.post("/", response_model=SchemesResponse, summary="Find government schemes for farmers")
def get_schemes(req: SchemesRequest):
    """
    Ask about any Indian government agricultural scheme:
    - PM-KISAN income support
    - PM Fasal Bima Yojana (crop insurance)
    - Soil Health Card
    - Kisan Credit Card
    - PMKSY (irrigation subsidy)
    - State-specific schemes
    
    You can also describe your situation and ask what schemes you qualify for.
    """
    search_query = f"government scheme {req.query}"
    if req.state: search_query += f" {req.state}"

    results = retrieve(search_query)
    context = format_context(results)
    sources = list({src for _, src, _ in results})

    parts = [f"Question about government schemes: {req.query}"]
    if req.state:       parts.append(f"State: {req.state}")
    if req.farmer_type: parts.append(f"Farmer type: {req.farmer_type}")

    result = ask_watsonx(
        user_message="\n".join(parts),
        context=context,
        language=req.language,
        extra_instructions=SCHEMES_INSTRUCTIONS,
    )

    return SchemesResponse(
        answer=result["answer"],
        sources=sources,
        language_used=result["language_used"],
        mode=result["source"],
    )


@schemes_router.get("/list", summary="List all known schemes in the knowledge base")
def list_schemes():
    """Quick reference list of schemes in the system."""
    return {
        "schemes": [
            {"name": "PM-KISAN",       "benefit": "₹6,000/year income support", "apply": "pmkisan.gov.in"},
            {"name": "PMFBY",          "benefit": "Crop insurance at low premium", "apply": "pmfby.gov.in"},
            {"name": "Kisan Credit Card", "benefit": "Loan up to ₹3L at 4% interest", "apply": "Any bank"},
            {"name": "Soil Health Card",  "benefit": "Free soil testing + recommendation", "apply": "Nearest KVK"},
            {"name": "PMKSY",          "benefit": "Drip/sprinkler irrigation subsidy", "apply": "State agriculture dept"},
            {"name": "eNAM",           "benefit": "Online crop market access", "apply": "enam.gov.in"},
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APP (from main.py)
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="FarmAI — Crop Assistant API",
    description=(
        "AI-powered assistant for farmers using FAISS knowledge retrieval + IBM watsonx.\n\n"
        "Features: crop Q&A, disease diagnosis, weather advice, government schemes, multilingual, offline-capable."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router,    prefix="/api/chat",    tags=["💬 Crop Chat"])
app.include_router(disease_router, prefix="/api/disease", tags=["🌿 Disease Diagnosis"])
app.include_router(weather_router, prefix="/api/weather", tags=["🌦 Weather Advice"])
app.include_router(schemes_router, prefix="/api/schemes", tags=["📋 Govt Schemes"])


@app.get("/", tags=["Health"])
def root():
    """Redirects to the FarmAI web interface."""
    return RedirectResponse(url="/ui")


@app.get("/ui", response_class=HTMLResponse, tags=["UI"])
def ui():
    """Serve the FarmAI web interface."""
    html_path = Path(__file__).resolve().parent / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"), status_code=200)


@app.get("/health", tags=["Health"])
def health():
    """Quick health check — also verifies FAISS index is loaded."""
    return {"status": "ok", "knowledge_base": get_index_stats()}


# ═══════════════════════════════════════════════════════════════════════════════
# BUILD INDEX CLI (from build_index.py)
# ═══════════════════════════════════════════════════════════════════════════════

def run_build_index():
    """
    Run this to build the FAISS index.

    Usage (from command line):
        python app.py build           # build from data/docs/ + seed knowledge
        python app.py build --force   # force rebuild even if index exists
    """
    force = "--force" in sys.argv
    print("=" * 50)
    print("FarmAI — FAISS Index Builder")
    print("=" * 50)
    build_index(force=force)
    stats = get_index_stats()
    print(f"\n✅ Done! Index stats: {stats}")
    print("\nYou can now start the server with:")
    print("  uvicorn app:app --reload --port 8000")


# ═══════════════════════════════════════════════════════════════════════════════
# EMBEDDED NON-PYTHON FILES
# ═══════════════════════════════════════════════════════════════════════════════

REQUIREMENTS_TXT = """\
# ── Web Framework ─────────────────────────────────────────────────────────────
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
python-dotenv==1.0.1

# ── IBM watsonx AI ────────────────────────────────────────────────────────────
ibm-watsonx-ai==1.1.2

# ── FAISS (vector search — offline knowledge retrieval) ───────────────────────
faiss-cpu==1.8.0          # CPU version — use faiss-gpu if you have CUDA

# ── Embeddings (local NLP model — runs fully offline after first download) ────
sentence-transformers==3.1.1
torch==2.4.1               # required by sentence-transformers

# ── Utilities ─────────────────────────────────────────────────────────────────
numpy==1.26.4
httpx==0.27.2
"""

ENV_EXAMPLE = """\
# ── IBM watsonx Credentials ───────────────────────────────────────────────────
# Get these from: https://cloud.ibm.com → watsonx.ai → Project settings

IBM_API_KEY=your_ibm_api_key_here
IBM_PROJECT_ID=your_project_id_here
IBM_URL=https://us-south.ml.cloud.ibm.com

# Model options (pick one):
#   ibm/granite-13b-instruct-v2      ← recommended, fast
#   meta-llama/llama-3-70b-instruct  ← best quality
#   mistralai/mistral-large          ← good multilingual
IBM_MODEL_ID=ibm/granite-13b-instruct-v2
"""

SAMPLE_KNOWLEDGE_JSON = """\
[
  {
    "text": "Wheat rust (Yellow rust / Brown rust / Black rust) is a fungal disease caused by Puccinia species. Yellow rust appears as yellow-orange pustules in stripes on leaves. Brown rust shows circular orange-brown pustules on upper leaf surface. Black rust appears as dark reddish-brown pustules on stems and leaves. All three spread through wind-borne spores. Control: Propiconazole 25 EC @ 0.1% (1 ml/L) or Tebuconazole 25 WG @ 1 g/L. Spray at first sign of disease. Resistant varieties: HD-2967, PBW-343, HD-3086.",
    "lang": "en",
    "topic": "wheat_rust_disease"
  },
  {
    "text": "PM-KISAN Samman Nidhi Yojana: Eligibility - all landholding farmer families with cultivable land. Benefit: Rs 6,000 per year in three equal installments of Rs 2,000 each (April-July, August-November, December-March). How to apply: Visit pmkisan.gov.in or nearest Common Service Centre (CSC). Documents needed: Aadhaar card, bank account number, land records (Khasra/Khatauni). Helpline: 155261 or 1800-115-526 (toll free).",
    "lang": "en",
    "topic": "pm_kisan_scheme"
  },
  {
    "text": "गेहूं की किट्ट (रस्ट) बीमारी: पीली किट्ट में पत्तियों पर पीले-नारंगी रंग के धब्बे होते हैं। नियंत्रण: Propiconazole 25 EC 1 मि.ली. प्रति लीटर पानी में मिलाकर छिड़काव करें। बीमारी दिखते ही तुरंत उपाय करें। प्रतिरोधी किस्में: HD-2967, PBW-343 बोएं।",
    "lang": "hi",
    "topic": "wheat_rust_hi"
  },
  {
    "text": "Drip Irrigation subsidy under PMKSY (Pradhan Mantri Krishi Sinchayee Yojana): Small and marginal farmers get 55% subsidy on drip/sprinkler system cost. Other farmers get 45% subsidy. Apply at your District Agriculture Office or online at your state agriculture department portal. Benefits: saves 40-60% water, increases yield by 20-50%, reduces weed growth, suitable for vegetables, fruits, sugarcane, cotton.",
    "lang": "en",
    "topic": "pmksy_drip_subsidy"
  }
]
"""

README_MD = """\
# 🌾 FarmAI — Crop Assistant API
### Gen AI Hackathon | Python · FastAPI · FAISS · IBM watsonx · NLP

> AI-powered assistant for farmers: crop Q&A, disease diagnosis, weather advice,
> government schemes — multilingual, offline-capable, RAG-powered.

---

## 🏗️ Architecture

```
Farmer's Query (any language)
         │
         ▼
   ┌─────────────┐
   │  FastAPI     │  ← REST API (4 endpoints)
   └──────┬──────┘
          │
          ▼
   ┌─────────────────────────┐
   │  FAISS Knowledge Search │  ← Local vector DB (works OFFLINE)
   │  sentence-transformers  │    Searches crop/pest/scheme docs
   └──────────┬──────────────┘
              │  Top-K relevant chunks
              ▼
   ┌─────────────────────────┐
   │  IBM watsonx.ai         │  ← Granite / Llama 3 / Mistral
   │  (RAG-augmented prompt) │    Generates final answer
   └──────────┬──────────────┘
              │  Falls back if offline ↓
   ┌─────────────────────────┐
   │  Offline Fallback       │  ← Returns FAISS results directly
   │  (raw knowledge mode)   │    No internet needed
   └─────────────────────────┘
              │
              ▼
   Multilingual Response (en/hi/te/ta/mr/kn/gu/pa/bn)
```

---

## 📁 Single-File Structure (Merged)

This file (`app.py`) contains everything:
- IBM watsonx service
- FAISS RAG service
- Chat router
- Disease router
- Weather router
- Schemes router
- FastAPI app
- Build index CLI
- Embedded: requirements.txt, .env.example, sample_knowledge.json

---

## ⚡ Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up IBM watsonx credentials
```bash
cp .env.example .env
# Edit .env with your IBM API key and Project ID
```

### 3. Build the FAISS knowledge index
```bash
python app.py build
```

### 4. Start the API server
```bash
uvicorn app:app --reload --port 8000
```

### 5. Open interactive docs
**http://localhost:8000/docs** — Swagger UI, test all endpoints live

---

## 🔌 API Endpoints

- `POST /api/chat/`        — General crop Q&A
- `POST /api/disease/`     — Disease diagnosis
- `POST /api/weather/advice` — Weather-aware advice
- `POST /api/schemes/`     — Government scheme lookup
- `GET  /api/schemes/list` — All known schemes
- `GET  /health`           — Health check

---

## 📴 Offline Capability

| Component | Online | Offline |
|-----------|--------|---------|
| FAISS retrieval | ✅ | ✅ (runs locally) |
| Embeddings (sentence-transformers) | ✅ | ✅ (local model) |
| IBM watsonx generation | ✅ | ❌ (needs internet) |
| Offline fallback | — | ✅ returns raw knowledge |

---

## 📞 Farmer Helpline
Kisan Call Centre: **1800-180-1551** (free, 24x7, 22 languages)
"""


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        run_build_index()
    else:
        print("FarmAI — Single-File App")
        print("Usage:")
        print("  python app.py build [--force]   → Build FAISS index")
        print("  uvicorn app:app --reload --port 8000  → Start server")
