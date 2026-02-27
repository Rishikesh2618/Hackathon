"""
/api/schemes — Government agricultural scheme lookup using FAISS + IBM watsonx.
Helps farmers discover and understand schemes they're eligible for.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.services.rag_service import retrieve, format_context
from app.services.ibm_service import ask_watsonx

router = APIRouter()

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


@router.post("/", response_model=SchemesResponse, summary="Find government schemes for farmers")
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


@router.get("/list", summary="List all known schemes in the knowledge base")
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
