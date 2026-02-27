from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, disease, weather, schemes

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

app.include_router(chat.router,    prefix="/api/chat",    tags=["💬 Crop Chat"])
app.include_router(disease.router, prefix="/api/disease", tags=["🌿 Disease Diagnosis"])
app.include_router(weather.router, prefix="/api/weather", tags=["🌦 Weather Advice"])
app.include_router(schemes.router, prefix="/api/schemes", tags=["📋 Govt Schemes"])


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online 🌾",
        "message": "FarmAI is running — FAISS + IBM watsonx powered",
        "endpoints": ["/api/chat", "/api/disease", "/api/weather", "/api/schemes"],
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    """Quick health check — also verifies FAISS index is loaded."""
    from app.services.rag_service import get_index_stats
    return {"status": "ok", "knowledge_base": get_index_stats()}
