"""
build_index.py — Run this ONCE before starting the server to build the FAISS index.

Usage:
    python build_index.py           # build from data/docs/ + seed knowledge
    python build_index.py --force   # force rebuild even if index exists

Add your own knowledge:
    Place .txt or .json files in data/docs/
    .json format: [{"text": "...", "lang": "en", "topic": "wheat_pests"}, ...]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.rag_service import build_index, get_index_stats

if __name__ == "__main__":
    force = "--force" in sys.argv
    print("=" * 50)
    print("FarmAI — FAISS Index Builder")
    print("=" * 50)
    build_index(force=force)
    stats = get_index_stats()
    print(f"\n✅ Done! Index stats: {stats}")
    print("\nYou can now start the server with:")
    print("  uvicorn app.main:app --reload --port 8000")
