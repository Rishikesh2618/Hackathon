"""
Translation helper for FarmAI multilingual support.
Uses deep-translator (Google Translate backend) – works offline-friendly via cache.
"""

import json
from pathlib import Path

CACHE_FILE = Path("model_cache") / "translation_cache.json"

_cache: dict = {}

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi (हिंदी)",
    "te": "Telugu (తెలుగు)",
    "ta": "Tamil (தமிழ்)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "mr": "Marathi (मराठी)",
    "bn": "Bengali (বাংলা)",
    "gu": "Gujarati (ગુજરાતી)",
    "pa": "Punjabi (ਪੰਜਾਬੀ)",
    "ml": "Malayalam (മലയാളം)",
}


def _load_cache():
    global _cache
    if CACHE_FILE.exists():
        try:
            _cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            _cache = {}


def _save_cache():
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(_cache, ensure_ascii=False, indent=2), encoding="utf-8")


_load_cache()


def translate_text(text: str, source_lang: str = "auto", target_lang: str = "en") -> str:
    """Translate text using Google Translate via deep-translator. Caches results."""
    if target_lang == source_lang or target_lang == "en" and source_lang == "en":
        return text
    if not text or not text.strip():
        return text

    cache_key = f"{source_lang}|{target_lang}|{text[:200]}"
    if cache_key in _cache:
        return _cache[cache_key]

    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        result = translator.translate(text)
        if result:
            _cache[cache_key] = result
            _save_cache()
            return result
    except Exception as e:
        print(f"[Translation] Error: {e}")

    return text   # fallback: return original


def detect_language(text: str) -> str:
    """Detect the language of the input text."""
    try:
        from langdetect import detect
        return detect(text)
    except Exception:
        return "en"


def get_supported_languages():
    return SUPPORTED_LANGUAGES
