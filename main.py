"""
FarmAI - Main FastAPI Application
Generative AI system for Indian farmers answering queries about
crops, pests, fertilizers, and government schemes.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import time
import os

# ── Local modules ──────────────────────────────────────────────
from vector_engine import build_index, semantic_search, get_answer
from translator import translate_text, detect_language, get_supported_languages
from knowledge_base import get_by_category, get_categories, KNOWLEDGE_BASE

# ── App setup ──────────────────────────────────────────────────
app = FastAPI(
    title="FarmAI",
    description="Generative AI for Indian Farmers – Crops, Pests, Fertilizers & Schemes",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


# ── Pydantic models ────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    language: Optional[str] = "en"   # user's preferred language
    category: Optional[str] = None   # crops | pests | fertilizers | schemes | general
    top_k: Optional[int] = 3


class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str = "en"


class FeedbackRequest(BaseModel):
    query_id: str
    helpful: bool
    comment: Optional[str] = ""


# ── Routes ─────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("frontend/index.html")


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "FarmAI",
        "timestamp": time.time(),
        "message": "Jai Kisan! 🌾",
    }


@app.post("/api/query")
async def handle_query(request: QueryRequest):
    """
    Main endpoint: accepts a farmer's question, performs semantic search,
    and returns an AI-generated answer with source references.
    Supports multilingual input/output.
    """
    raw_query = request.query.strip()
    if not raw_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    user_lang = request.language or "en"

    # 1. Detect language if not specified / detect if auto
    detected_lang = detect_language(raw_query) if user_lang == "auto" else user_lang

    # 2. Translate query to English for FAISS search
    english_query = raw_query
    if detected_lang != "en":
        english_query = translate_text(raw_query, source_lang=detected_lang, target_lang="en")

    # 3. Retrieve answer from knowledge base
    category = request.category if request.category and request.category != "all" else None
    result   = get_answer(english_query, top_k=request.top_k, category_filter=category)

    # 4. Translate answer back to user's language
    answer_text = result["answer"]
    if user_lang not in ("en", "auto"):
        answer_text = translate_text(answer_text, source_lang="en", target_lang=user_lang)

    # 5. Build structured response
    sources_out = []
    for src in result["sources"]:
        sources_out.append({
            "id":       src["id"],
            "title":    src["title"],
            "category": src["category"],
            "score":    src["score"],
            "snippet":  src["content"][:250] + "…",
        })

    return {
        "query":          raw_query,
        "english_query":  english_query,
        "answer":         answer_text,
        "sources":        sources_out,
        "confidence":     result["confidence"],
        "detected_lang":  detected_lang,
        "response_lang":  user_lang,
    }


@app.get("/api/schemes")
async def list_schemes(lang: str = Query("en")):
    """List all government schemes with optional translation."""
    items = get_by_category("schemes")
    schemes = []
    for item in items:
        title   = item["title"]
        content = item["content"][:300] + "…"
        if lang != "en":
            title   = translate_text(title,   source_lang="en", target_lang=lang)
            content = translate_text(content, source_lang="en", target_lang=lang)
        schemes.append({
            "id":       item["id"],
            "title":    title,
            "summary":  content,
            "keywords": item["keywords"][:5],
        })
    return {"count": len(schemes), "schemes": schemes}


@app.get("/api/categories")
async def list_categories():
    """Return available knowledge categories."""
    cats = get_categories()
    label_map = {
        "crops":       "🌾 Crops",
        "pests":       "🐛 Pests & Diseases",
        "fertilizers": "🧪 Fertilizers",
        "schemes":     "🏛️ Govt Schemes",
        "general":     "📚 General Agriculture",
    }
    return {
        "categories": [
            {"key": c, "label": label_map.get(c, c.title())} for c in sorted(cats)
        ]
    }


@app.get("/api/languages")
async def list_languages():
    """Return supported languages for multilingual Q&A."""
    return {"languages": get_supported_languages()}


@app.post("/api/translate")
async def translate_endpoint(request: TranslateRequest):
    """Translate any text between supported languages."""
    translated = translate_text(
        request.text,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
    )
    return {"original": request.text, "translated": translated, "target_lang": request.target_lang}


@app.get("/api/suggestions")
async def get_suggestions(lang: str = Query("en")):
    """Return pre-built example questions for quick access."""
    suggestions = [
        "How do I grow rice in waterlogged soil?",
        "What is the best fertilizer for wheat?",
        "How to control Fall Armyworm in maize?",
        "Tell me about PM-KISAN scheme eligibility",
        "How to apply for Kisan Credit Card?",
        "What are the symptoms of zinc deficiency in crops?",
        "How to do drip irrigation in cotton?",
        "What is the MSP for paddy in 2024?",
        "How to control brown plant hopper in rice?",
        "Tell me about organic farming schemes",
    ]
    if lang != "en":
        suggestions = [translate_text(s, source_lang="en", target_lang=lang) for s in suggestions]
    return {"suggestions": suggestions}


@app.get("/api/knowledge/{doc_id}")
async def get_document(doc_id: str, lang: str = Query("en")):
    """Get full details of a specific knowledge document."""
    for item in KNOWLEDGE_BASE:
        if item["id"] == doc_id:
            title   = item["title"]
            content = item["content"]
            if lang != "en":
                title   = translate_text(title,   source_lang="en", target_lang=lang)
                content = translate_text(content, source_lang="en", target_lang=lang)
            return {
                "id":       item["id"],
                "category": item["category"],
                "title":    title,
                "content":  content,
                "keywords": item["keywords"],
            }
    raise HTTPException(status_code=404, detail="Document not found")


# ── Startup event ──────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    print("[FarmAI] Starting up – building FAISS index …")
    build_index()
    print("[FarmAI] Ready to serve farmers! 🌾")


# ── Entry point ────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
