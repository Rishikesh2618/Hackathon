"""
setup_pipeline.py
Run this once to prepare all data, embeddings, and FAISS index.
Usage:  python setup_pipeline.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def main():
    print("=" * 60)
    print("  Kisan Call Centre Query Assistant – Setup Pipeline")
    print("=" * 60)

    # ── Step 1: Preprocess data ─────────────────────────────────────────
    print("\n[Step 1/3] Preprocessing raw KCC data...")
    from services.preprocess_data import preprocess_data
    preprocess_data(
        input_csv="data/raw_kcc.csv",
        output_csv="data/clean_kcc.csv",
        output_json="data/kcc_qa_pairs.json",
    )

    # ── Step 2: Generate embeddings ─────────────────────────────────────
    print("\n[Step 2/3] Generating embeddings (this may take a minute)...")
    from services.generate_embeddings import generate_embeddings
    generate_embeddings(
        input_json="data/kcc_qa_pairs.json",
        output_pickle="embeddings/kcc_embeddings.pkl",
    )

    # ── Step 3: Build FAISS index ───────────────────────────────────────
    print("\n[Step 3/3] Building FAISS vector index...")
    from vector_store.faiss_indexer import FAISSVectorStore
    vs = FAISSVectorStore(dim=384)
    vs.build_index("embeddings/kcc_embeddings.pkl")
    vs.save_index()

    print("\n" + "=" * 60)
    print("  ✓  Setup complete!")
    print("  Run the app with:  streamlit run ui/app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
