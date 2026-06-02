# ScriptForge — AI Content Generation Platform

A production-ready, multi-agent content platform. Enter one idea — get a production-ready video script and platform-specific assets across YouTube, LinkedIn, X/Twitter, Newsletter, and SEO Blog automatically.

**Live app:** [scriptforge-eosin.vercel.app](https://scriptforge-eosin.vercel.app)  
**Stack:** React + TypeScript · Python FastAPI · OpenAI GPT-4o · Claude Sonnet · n8n · Vercel · Google Cloud Run

---

## What it does

A content strategist enters:
- A topic or content idea
- A tone (Dramatic / Neutral / Uplifting)
- A target video length (1 / 3 / 5 / 10 minutes)
- Output platforms (YouTube, LinkedIn, Twitter, Newsletter, SEO Blog)

ScriptForge runs a multi-agent AI pipeline and returns a fully structured script plus platform-specific content for every selected channel — ready to review, approve, and publish.

---

## Architecture

```
User Input
    ↓
React + TypeScript Frontend  (Vercel)
    ↓ POST /api/generate
Python FastAPI Backend  (Google Cloud Run)
    ↓
OpenAI GPT-4o  →  Initial script generation
    ↓
Claude Sonnet  →  Tone refinement & quality pass
    ↓
Validation Layer
    ↓
Claude Sonnet  →  Parallel platform formatting (asyncio.gather)
    ↓
PostgreSQL  →  Content storage (Neon)
    ↓
[On approval] n8n Webhook  →  Slack · Google Doc · CMS · Schedule
```

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite |
| Backend | Python 3.12 + FastAPI |
| AI — generation | OpenAI GPT-4o |
| AI — refinement | Anthropic Claude Sonnet |
| Database | PostgreSQL (Neon) |
| Automation | n8n |
| Frontend hosting | Vercel |
| Backend hosting | Google Cloud Run |
| Containerisation | Docker + Artifact Registry |
| CI/CD | GitHub Actions (4-stage pipeline) |

---

## CI/CD Pipeline

Every push to main triggers a 4-stage pipeline:

```
Push to main
     ↓
Job 1: Frontend — npm ci + tsc + vite build
Job 2: Backend  — pip install + ruff lint + mypy type check
     ↓ (both must pass)
Job 3: Docker   — build image + push to Artifact Registry
     ↓
Job 4: Deploy   — Google Cloud Run auto-deployment
```

---

## Key engineering decisions

**Why two AI models?**
GPT-4o handles creative generation. Claude handles tone refinement and platform formatting. Each model does what it's better at — specialisation, not redundancy.

**Why asyncio.gather for platform formatting?**
Platform jobs are independent. Running them concurrently reduces formatting time from O(n) to roughly O(1).

**Why the pipeline is isolated in orchestrator/pipeline.py**
The pipeline is completely separated from the HTTP layer. It can be triggered from a route, background job, or n8n webhook without any code changes.

**Retry logic**
Every API call uses exponential backoff (2^attempt seconds). Rate limits and API errors are caught separately. After max retries the error propagates cleanly as a 502.

**Prompt versioning**
Tone instructions live in config objects — brand voice updates are one-line changes, not code changes.

---

## Local development

```bash
# Backend
cd backend
cp .env.example .env      # fill in your API keys
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
cp .env.example .env
npm install
npm run dev
```

App runs at `http://localhost:3000`

---

## Deployment

**Frontend → Vercel**
```bash
cd frontend && vercel
```

**Backend → Google Cloud Run**
```bash
gcloud run deploy scriptforge-api --source ./backend --region us-east1 --allow-unauthenticated
```

Or push to main — the GitHub Actions pipeline deploys automatically.

---

## Environment variables

**Backend `.env`**
```
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
N8N_WEBHOOK_URL=https://your-n8n-webhook-url
DATABASE_URL=postgresql://user:password@host:5432/scriptforge
```

**Frontend `.env`**
```
VITE_API_URL=
```

---

## Automation (n8n)

Import `n8n/workflows/content_approved.json` into your n8n instance. On content approval the workflow triggers in parallel:

- Slack notification to `#content-approvals`
- Google Doc created with all assets
- CMS scheduling endpoint called
- Team notified

---

## Author

**Joshua Izategbese**  
Full Stack Developer  
GitHub: [github.com/Josueize](https://github.com/Josueize)  
Email: izategbese1@gmail.com
