<div align="center">
  <img src="infinit.png" alt="Infinit Logo" width="120" />
  <h1>Infinit</h1>
  <p><strong>Local AI tutoring for K–8 STEM learners</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-5887FF?style=flat-square&logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/React-18-A682FF?style=flat-square&logo=react&logoColor=white" />
    <img src="https://img.shields.io/badge/FastAPI-latest-715AFF?style=flat-square&logo=fastapi&logoColor=white" />
    <img src="https://img.shields.io/badge/Ollama-local-55C1FF?style=flat-square" />
    <img src="https://img.shields.io/badge/ChromaDB-vector%20store-102E4A?style=flat-square" />
  </p>
</div>

---

Infinit is a locally-running STEM tutoring platform built for K–8 students and educators. It combines a fine-tuned language model, a 30,000-entry RAG knowledge base, and an interactive React frontend — all running entirely on your machine with no cloud dependency.

## Features

- **Four model versions** (V1–V4) with progressive capability — from basic Q&A to fine-tuned RAG with confidence scoring
- **RAG via ChromaDB** — 30,000+ STEM entries aligned to NGSS, CCSS, and CSTA standards, embedded with `nomic-embed-text`
- **Custom fine-tuned model** (`infinit-v4`) with strict physics, chemistry, biology, and earth science reasoning rules
- **Quiz mode** — generates multi-choice questions from any topic, with per-question explanations
- **Hint & Socratic modes** — guided discovery instead of direct answers
- **Grade selector** — responses adapt to K–3, 4–6, and 7–8 reading levels
- **Follow-up questions** — automatically checks student understanding after each answer
- **Content filter** — blocks inappropriate queries before they reach the model
- **Analytics endpoint** — tracks grade distribution, mode usage, and top STEM keywords (no PII stored)
- **File upload support** — students can paste or upload assignments for contextual help

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · FastAPI · LangChain |
| Frontend | React 18 · Vite |
| Model serving | Ollama (`infinit-v4`, `mathstral:7b`) |
| Vector store | ChromaDB |
| Embeddings | `nomic-embed-text` |
| Web search (optional) | Tavily API |

## Project Structure

```
infinit/
├── server.py                  # FastAPI backend — all routes and model logic
├── V1.py – V4.py              # Standalone model iterations (reference)
├── VectorV1.py / VectorV2.py  # Vector store setup scripts
├── ingest_v4_database.py      # One-time ingestion script for scibot_v4 collection
├── infinit_upgrades.py        # Drop-in helper: query classifier, confidence scoring, citations
├── stem_k12_rag_dataset.csv   # 30,000-entry STEM knowledge base (NGSS/CCSS/CSTA)
├── science_rag_database.csv   # Science-focused RAG dataset (V3/V4)
├── Modelfile                  # Ollama Modelfile for infinit-v4
├── infinit-chatbot.jsx        # React frontend component
├── StartInfinit.command       # macOS launcher script
└── chroma_db/                 # Persisted ChromaDB vector store (generated)
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- [Ollama](https://ollama.com) installed and running

### 1. Install Python dependencies

```bash
pip install fastapi uvicorn langchain langchain-chroma langchain-ollama chromadb python-dotenv tavily-python httpx pandas
```

### 2. Pull the base model and create infinit-v4

```bash
ollama pull nomic-embed-text
ollama create infinit-v4 -f Modelfile
```

### 3. Ingest the knowledge base

```bash
python ingest_v4_database.py
```

This runs once and builds the ChromaDB vector store from `science_rag_database.csv`.

### 4. Start the backend

```bash
uvicorn server:app --reload --port 8000
```

### 5. Start the frontend

```bash
npm install
npm run dev
```

Or on macOS, double-click `StartInfinit.command`.

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/models` | List available model versions |
| `POST` | `/chat` | Single-turn response |
| `POST` | `/chat/stream` | Streaming response (SSE) |
| `POST` | `/chat/grade` | Preview grade-calibrated approach |
| `GET` | `/analytics` | Aggregate usage stats |

### Example request

```json
POST /chat/stream
{
  "question": "How does photosynthesis work?",
  "model": "v4",
  "mode": "normal",
  "grade_level": "46"
}
```

**Modes:** `normal` · `quiz` · `socratic` · `hint`  
**Grade levels:** `k3` · `46` · `78`

## Model Versions

| Version | Description |
|---|---|
| V1 | Baseline LLM, no RAG |
| V2 | RAG with `Science_RAG_DB`, improved system prompt |
| V3 | ChromaDB retrieval, follow-up questions, off-topic detection |
| V4 | Fine-tuned `infinit-v4`, 30K-entry STEM dataset, confidence scoring, all modes |

## Color Palette

| Swatch | Hex | Role |
|---|---|---|
| ![](https://img.shields.io/badge/-A682FF-A682FF?style=flat-square) | `#A682FF` | Primary / lavender |
| ![](https://img.shields.io/badge/-715AFF-715AFF?style=flat-square) | `#715AFF` | Accent / deep violet |
| ![](https://img.shields.io/badge/-5887FF-5887FF?style=flat-square) | `#5887FF` | Secondary / periwinkle |
| ![](https://img.shields.io/badge/-55C1FF-55C1FF?style=flat-square) | `#55C1FF` | Info / sky blue |
| ![](https://img.shields.io/badge/-102E4A-102E4A?style=flat-square) | `#102E4A` | Background / navy |

