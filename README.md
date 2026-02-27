# 🌾 FarmAI — Crop Assistant API
### Gen AI Hackathon | Python · FastAPI · FAISS · IBM watsonx · NLP

> AI-powered assistant for farmers: crop Q&A, disease diagnosis, weather advice,
> government schemes — multilingual, offline-capable, RAG-powered.

---

## 🏗️ Architecture

```
Farmer's Query (any language)
         │
         ▼
   ┌─────────────┐
   │  FastAPI     │  ← REST API (4 endpoints)
   └──────┬──────┘
          │
          ▼
   ┌─────────────────────────┐
   │  FAISS Knowledge Search │  ← Local vector DB (works OFFLINE)
   │  sentence-transformers  │    Searches crop/pest/scheme docs
   └──────────┬──────────────┘
              │  Top-K relevant chunks
              ▼
   ┌─────────────────────────┐
   │  IBM watsonx.ai         │  ← Granite / Llama 3 / Mistral
   │  (RAG-augmented prompt) │    Generates final answer
   └──────────┬──────────────┘
              │  Falls back if offline ↓
   ┌─────────────────────────┐
   │  Offline Fallback       │  ← Returns FAISS results directly
   │  (raw knowledge mode)   │    No internet needed
   └─────────────────────────┘
              │
              ▼
   Multilingual Response (en/hi/te/ta/mr/kn/gu/pa/bn)
```

---

## 📁 Project Structure

```
farmai/
├── app/
│   ├── main.py                      # FastAPI app + router registration
│   ├── routers/
│   │   ├── chat.py                  # /api/chat    — General Q&A
│   │   ├── disease.py               # /api/disease — Disease diagnosis
│   │   ├── weather.py               # /api/weather — Weather advice
│   │   └── schemes.py               # /api/schemes — Govt schemes
│   └── services/
│       ├── rag_service.py           # FAISS index build + retrieval
│       └── ibm_service.py           # IBM watsonx API wrapper + offline fallback
├── data/
│   └── docs/                        # ← Add your knowledge documents here
│       └── sample_knowledge.json    # Sample: diseases, schemes, crops
├── build_index.py                   # Run ONCE to build FAISS index
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚡ Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up IBM watsonx credentials
```bash
cp .env.example .env
# Edit .env with your IBM API key and Project ID
```

Get credentials: **https://cloud.ibm.com → watsonx.ai → Projects → Manage**

### 3. Build the FAISS knowledge index
```bash
python build_index.py
# Output: ✅ Done! Index stats: {vectors: 87, chunks: 87}
```

### 4. Start the API server
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Open interactive docs
**http://localhost:8000/docs** — Swagger UI, test all endpoints live

---

## 🔌 API Endpoints

### `POST /api/chat/` — General Crop Chat
```json
// Request
{
  "message": "When should I apply urea to wheat?",
  "language": "hi",
  "history": []
}

// Response
{
  "reply": "गेहूं में यूरिया को दो बार डालना चाहिए...",
  "sources": ["wheat_basics", "fertilizer_nitrogen"],
  "language_used": "Hindi",
  "mode": "ibm_watsonx"
}
```

---

### `POST /api/disease/` — Disease Diagnosis
```json
// Request
{
  "crop": "tomato",
  "symptoms": "Yellow-brown spots on leaves, white fungal growth underneath, spreading fast after rain",
  "growth_stage": "fruiting",
  "language": "te",
  "additional_info": "Heavy rain last 3 days, high humidity"
}

// Response
{
  "crop": "tomato",
  "diagnosis": "TOP SUSPECTED DISEASE: Late Blight (Phytophthora infestans)...",
  "sources": ["late_blight"],
  "language_used": "Telugu",
  "mode": "ibm_watsonx"
}
```

---

### `POST /api/weather/advice` — Weather-Aware Advice
```json
// Request
{
  "crop": "wheat",
  "crop_stage": "flowering",
  "planned_activity": "spray fungicide",
  "location": "Punjab",
  "language": "pa",
  "weather": {
    "temperature_c": 22,
    "humidity_percent": 85,
    "wind_speed_kmh": 8,
    "condition": "cloudy",
    "forecast_next_days": "Rain expected tomorrow"
  }
}
```

---

### `POST /api/schemes/` — Government Scheme Lookup
```json
// Request
{
  "query": "crop insurance for kharif season",
  "state": "Maharashtra",
  "farmer_type": "small",
  "language": "mr"
}
```

### `GET /api/schemes/list` — All Known Schemes
Returns quick reference list of PM-KISAN, PMFBY, KCC, PMKSY, Soil Health Card, eNAM.

---

## 📚 Adding Your Own Knowledge

Place files in `data/docs/` then run `python build_index.py --force`:

**Text file** (`wheat_pests.txt`):
```
Aphids on wheat cause leaf curl and sticky residue...
Control: Imidacloprid 17.8 SL @ 0.5 ml/L water...
```

**JSON file** (`schemes_mp.json`):
```json
[
  {
    "text": "MP Kisan Anudan Yojana gives subsidy for farm equipment...",
    "lang": "hi",
    "topic": "mp_kisan_anudan"
  }
]
```

---

## 🌐 Supported Languages

| Code | Language | Code | Language |
|------|----------|------|----------|
| `en` | English  | `kn` | Kannada  |
| `hi` | Hindi    | `gu` | Gujarati |
| `te` | Telugu   | `pa` | Punjabi  |
| `ta` | Tamil    | `bn` | Bengali  |
| `mr` | Marathi  |      |          |

---

## 📴 Offline Capability

The system works at **two levels**:

| Component | Online | Offline |
|-----------|--------|---------|
| FAISS retrieval | ✅ | ✅ (runs locally) |
| Embeddings (sentence-transformers) | ✅ | ✅ (local model) |
| IBM watsonx generation | ✅ | ❌ (needs internet) |
| Offline fallback | — | ✅ returns raw knowledge |

In low-connectivity areas, set up the server locally on a Raspberry Pi or laptop — FAISS + sentence-transformers run without internet after the first setup. Farmers get knowledge retrieval even without IBM watsonx.

---

## 🧪 curl Examples

```bash
# Chat in Telugu
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "వరి పంటకు ఏ ఎరువు వేయాలి?", "language": "te"}'

# Disease diagnosis
curl -X POST http://localhost:8000/api/disease/ \
  -H "Content-Type: application/json" \
  -d '{"crop": "rice", "symptoms": "Brown spots, stunted growth", "language": "hi"}'

# Scheme lookup
curl -X POST http://localhost:8000/api/schemes/ \
  -H "Content-Type: application/json" \
  -d '{"query": "crop insurance", "state": "Punjab", "language": "pa"}'

# Health check
curl http://localhost:8000/health
```

---

## 🏆 Hackathon Demo Script (5 minutes)

1. **Show architecture** — "FAISS finds relevant knowledge, IBM watsonx generates the answer"
2. **Demo `/api/chat`** — Ask "wheat fertilizer schedule" in English, then Hindi
3. **Demo `/api/disease`** — Paste real disease symptoms, show structured diagnosis
4. **Demo `/api/schemes`** — "What schemes am I eligible for as a small farmer in Maharashtra?"
5. **Show offline mode** — Disconnect internet, show FAISS fallback still returns knowledge
6. **Show `/docs`** — Clean Swagger UI = production-ready

---

## 📞 Farmer Helpline Integration
Kisan Call Centre: **1800-180-1551** (free, 24x7, 22 languages)
Always shown in offline fallback responses.
