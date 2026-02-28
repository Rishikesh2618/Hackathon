# 🌾 Kisan Call Centre Query Assistant

An AI-Powered Agricultural Helpdesk using **IBM Watsonx Granite LLM** and **FAISS**.

---

## Project Overview

The **Kisan Call Centre Query Assistant** is an intelligent agricultural query resolution system built for rural support and information dissemination. It leverages:

- **IBM Watsonx Granite LLM** (`ibm/granite-3-8b-instruct`) for natural language generation
- **FAISS** (Facebook AI Similarity Search) for fast semantic vector search
- **Sentence Transformers** (`all-MiniLM-L6-v2`) for embedding generation
- **Streamlit** for the interactive web frontend

The tool works in both **offline** (FAISS-only) and **online** (LLM-enhanced) modes.

---

## Project Structure

```
kisan_assistant/
├── data/
│   ├── raw_kcc.csv              # Raw KCC dataset (input)
│   ├── clean_kcc.csv            # Cleaned dataset (auto-generated)
│   └── kcc_qa_pairs.json        # Q&A pairs JSON (auto-generated)
│
├── embeddings/
│   └── kcc_embeddings.pkl       # Vector embeddings (auto-generated)
│
├── vector_store/
│   ├── faiss_indexer.py         # FAISSVectorStore class
│   ├── build_faiss.py           # Build FAISS index script
│   ├── faiss.index              # FAISS index file (auto-generated)
│   └── meta.pkl                 # Metadata store (auto-generated)
│
├── models/
│   └── granite_llm.py           # IBM Watsonx Granite LLM integration
│
├── services/
│   ├── preprocess_data.py       # Data cleaning pipeline
│   ├── generate_embeddings.py   # Embedding generation
│   └── query_handler.py         # Core RAG pipeline
│
├── ui/
│   └── app.py                   # Streamlit frontend
│
├── utils/
│   └── text_cleaning.py         # Shared text utilities
│
├── setup_pipeline.py            # One-shot setup script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md
```

---

## Prerequisites

- Python **3.9+**
- IBM Cloud account with **Watsonx** enabled
- VS Code or any Python IDE
- (Optional) Virtual environment

---

## Setup Instructions

### 1. Clone / Download the project

```bash
cd kisan_assistant
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure IBM Watsonx credentials

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_API_KEY=your_api_key_here
MODEL_ID=ibm/granite-3-8b-instruct
```

> **Note:** The app works in offline mode even without IBM credentials.

### 5. Run the setup pipeline (first time only)

```bash
python setup_pipeline.py
```

This will:
1. Preprocess `data/raw_kcc.csv` → `clean_kcc.csv` + `kcc_qa_pairs.json`
2. Generate sentence embeddings → `embeddings/kcc_embeddings.pkl`
3. Build FAISS index → `vector_store/faiss.index` + `vector_store/meta.pkl`

### 6. Launch the Streamlit app

```bash
streamlit run ui/app.py
```

Open your browser at **http://localhost:8501**

---

## How It Works

### Architecture

```
User Query
    │
    ▼
[Sentence Transformer]  ←── all-MiniLM-L6-v2
    │  (embed query)
    ▼
[FAISS Vector Store]    ←── Pre-indexed KCC Q&A embeddings
    │  (top-k retrieval)
    ▼
[Offline Answer]        ── Directly formatted retrieved Q&A
    │
    ├──► [Granite LLM]  ←── IBM Watsonx API (ibm/granite-3-8b-instruct)
    │         │  (RAG prompt)
    │         ▼
    │    [Online Answer] ── Natural language generation
    │
    ▼
[Streamlit UI]          ── Shows both answers side by side
```

### Pipeline Steps

| Step | Script | Description |
|------|--------|-------------|
| 1 | `preprocess_data.py` | Clean raw CSV → Q&A pairs |
| 2 | `generate_embeddings.py` | Embed Q&A with SentenceTransformer |
| 3 | `build_faiss.py` | Index embeddings with FAISS |
| 4 | `query_handler.py` | Embed query → retrieve top-k → build prompt |
| 5 | `granite_llm.py` | Send prompt to IBM Granite → parse response |
| 6 | `app.py` | Display offline + online answers in Streamlit |

---

## Sample Queries

| # | Query |
|---|-------|
| 1 | How to control aphids in mustard? |
| 2 | What is the treatment for leaf spot in tomato? |
| 3 | Suggest pesticide for whitefly in cotton. |
| 4 | How to prevent fruit borer in brinjal? |
| 5 | What fertilizer is recommended during flowering in maize? |
| 6 | How to protect paddy from blast disease? |
| 7 | What is the solution for jassids in cotton? |
| 8 | How to apply for PM Kisan Samman Nidhi scheme? |
| 9 | What is the dosage of neem oil for aphids? |
| 10 | How to treat blight in potato crops? |

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| LLM | IBM Watsonx Granite (`ibm/granite-3-8b-instruct`) |
| Embedding Model | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector Search | FAISS (Facebook AI Similarity Search) |
| Frontend | Streamlit |
| Language | Python 3.9+ |

---

## Extending the Project

- **Add more data**: Replace/augment `data/raw_kcc.csv` and re-run `setup_pipeline.py`
- **Add Hindi UI**: Wrap Streamlit with translation using `googletrans` or `indic-nlp`
- **Voice input**: Integrate `SpeechRecognition` library for voice queries
- **Deployment**: Deploy on Streamlit Cloud, AWS, or an Agri-kiosk device

---

## Credits

Built for **Kisan Call Centre (KCC)** rural support using AI/ML to bridge the knowledge gap for Indian farmers.

- **Platform**: SmartBridge × Smart Internz
- **Model**: IBM Watsonx Granite LLM
