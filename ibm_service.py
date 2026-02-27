"""
IBM watsonx AI Service.

Sends prompts to IBM watsonx.ai (granite or llama models) and returns responses.
Falls back to a local offline mode if IBM is unavailable (for low-connectivity environments).

IBM watsonx docs: https://www.ibm.com/products/watsonx-ai
Python SDK:       pip install ibm-watsonx-ai
"""

import os
from typing import Optional

# IBM SDK — install with: pip install ibm-watsonx-ai
try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    IBM_AVAILABLE = True
except ImportError:
    IBM_AVAILABLE = False
    print("[IBM] ibm-watsonx-ai not installed. Run: pip install ibm-watsonx-ai")


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


# ── Main function ─────────────────────────────────────────────────────────────

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
