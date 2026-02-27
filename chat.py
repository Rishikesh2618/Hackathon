"""
/api/chat — General crop Q&A with FAISS retrieval + IBM watsonx generation.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.services.rag_service import retrieve, format_context
from app.services.ibm_service import ask_watsonx, SUPPORTED_LANGUAGES

router = APIRouter()


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


@router.post("/", response_model=ChatResponse, summary="Ask FarmAI any crop question")
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


@router.get("/languages", summary="List supported languages")
def get_languages():
    return {"supported_languages": SUPPORTED_LANGUAGES}
