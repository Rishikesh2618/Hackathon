"""
/api/disease — Crop disease diagnosis from symptom descriptions.
Uses FAISS to retrieve matching disease knowledge before asking IBM watsonx.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.services.rag_service import retrieve, format_context
from app.services.ibm_service import ask_watsonx

router = APIRouter()

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


@router.post("/", response_model=DiagnosisResponse, summary="Diagnose disease from symptoms")
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
