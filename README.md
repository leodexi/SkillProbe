# SkillProbe AI

An AI-powered mock interview tool that reads your resume and asks you personalized technical questions — just like a real interviewer would.

---

## What It Does

1. You upload your resume as a PDF
2. The AI reads your resume and asks questions based on **your actual projects and skills**
3. You answer each question in a text box
4. The AI scores your answer on Technical Accuracy, Communication, and Problem Solving
5. At the end, you get a full performance report with strengths, weak areas, and study recommendations

Every question is grounded in your resume — so if you worked with React, JWT, or WebSockets, it asks about those specifically. It also adapts — if you give a weak answer, it asks a simpler follow-up on the same topic.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| AI / LLM | Ollama running `llama3.1` locally |
| Vector Search | ChromaDB (stores resume embeddings) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Session Storage | Redis |

---

## Prerequisites

Make sure you have these installed before starting:

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- **Ollama** — [ollama.com/download](https://ollama.com/download)
- **Redis** — via Docker (recommended) or [direct download](https://github.com/tporadowski/redis/releases)

---

## Setup

### 1. Clone / open the project

```
interviewPrep/
├── ai-service/     ← Python FastAPI backend
└── client/         ← React frontend
```

---

### 2. Set up the backend

```bash
cd ai-service

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file inside `ai-service/` (optional — defaults work fine locally):

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
CHROMA_PERSIST_DIR=./chroma_db
REDIS_URL=redis://localhost:6379
SESSION_TTL=86400
AI_SERVICE_PORT=8000
```

---

### 3. Set up the frontend

```bash
cd client
npm install
```

---

### 4. Pull the AI model

```bash
ollama pull llama3.1
```

This downloads `llama3.1` (~4.7GB) to your machine. Only needed once.

---

## Running the App

You need **4 things running** at the same time. Open 4 terminals:

### Terminal 1 — Redis
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```
> If you don't have Docker, download and run `redis-server.exe` from the link above.

### Terminal 2 — Ollama
```bash
ollama serve
```

### Terminal 3 — FastAPI Backend
```bash
cd ai-service
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 4 — React Frontend
```bash
cd client
npm run dev
```

---

### Open the app

Go to **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## How to Use

1. **Upload Resume** — click the upload box and select your PDF resume
2. Wait ~5–10 seconds while the AI processes and indexes your resume
3. **Answer Questions** — the AI will ask you technical questions one by one
4. Click **Submit Answer** after each response
5. Review your score and feedback for each question
6. Click **Next Question** to continue, or **Generate Report** to finish
7. View your **Performance Report** with overall score and recommendations

---

## Project Structure

```
ai-service/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Environment variables
│   ├── schemas.py               # Data models (Pydantic)
│   ├── store.py                 # Redis session storage
│   ├── routers/
│   │   └── interviews.py        # API endpoints
│   └── services/
│       ├── resume_processor.py  # PDF → embeddings → ChromaDB
│       ├── question_generator.py# LLM question generation (RAG)
│       ├── answer_evaluator.py  # LLM answer scoring
│       └── report_generator.py  # LLM final report
└── requirements.txt

client/
├── src/
│   ├── App.jsx                  # Main app state machine
│   ├── index.css                # Design system
│   └── components/
│       ├── Navbar.jsx
│       ├── UploadResume.jsx
│       ├── InterviewSession.jsx
│       ├── EvaluationCard.jsx
│       ├── ScoreGauge.jsx
│       └── FinalReport.jsx
└── vite.config.js
```

---

## Common Issues

**Question generation fails with connection error**
→ Ollama is not running. Start it with `ollama serve` in a terminal and keep it open.

**Upload works but session resets after server restart**
→ Make sure Redis is running. Without Redis, sessions are lost on restart.

**Resume text not extracted**
→ Your PDF might be image-based (scanned). The app only works with text-based PDFs.

**Very slow question generation**
→ Ollama runs on CPU by default. If you have an NVIDIA GPU, install CUDA drivers and Ollama will use it automatically — much faster.

---

## API Endpoints

| Method | Endpoint | What it does |
|---|---|---|
| `POST` | `/api/interviews/upload` | Upload resume PDF, start session |
| `POST` | `/api/interviews/{id}/question` | Generate next interview question |
| `POST` | `/api/interviews/{id}/answer` | Submit answer, get evaluation |
| `POST` | `/api/interviews/{id}/report` | Generate final performance report |
| `GET` | `/api/interviews/{id}` | Get current session state |
| `GET` | `/docs` | Interactive API docs (Swagger UI) |

**By Sid**
