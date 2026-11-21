# ScriptForge â€” AI Content Generation Platform

A production-ready, multi-agent content platform. Enter one idea â€” get a production-ready video script and platform-specific assets across YouTube, LinkedIn, X/Twitter, Newsletter, and SEO Blog automatically.

**Live app:** [scriptforge-eosin.vercel.app](https://scriptforge-eosin.vercel.app)  
**Stack:** React + TypeScript Â· Python FastAPI Â· OpenAI GPT-4o Â· Claude Sonnet Â· n8n Â· Vercel Â· Google Cloud Run

---

## What it does

A content strategist enters:
- A topic or content idea
- A tone (Dramatic / Neutral / Uplifting)
- A target video length (1 / 3 / 5 / 10 minutes)
- Output platforms (YouTube, LinkedIn, Twitter, Newsletter, SEO Blog)

ScriptForge runs a multi-agent AI pipeline and returns a fully structured script plus platform-specific content for every selected channel â€” ready to review, approve, and publish.

---

## Architecture

```
User Input
    â†“
React + TypeScript Frontend  (Vercel)
    â†“ POST /api/generate
Python FastAPI Backend  (Google Cloud Run)
    â†“
OpenAI GPT-4o  â†’  Initial script generation
    â†“
Claude Sonnet  â†’  Tone refinement & quality pass
    â†“
Validation Layer
    â†“
Claude Sonnet  â†’  Parallel platform formatting (asyncio.gather)
    â†“
PostgreSQL  â†’  Content storage (Neon)
    â†“
[On approval] n8n Webhook  â†’  Slack Â· Google Doc Â· CMS Â· Schedule
```

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite |
| Backend | Python 3.12 + FastAPI |
| AI â€” generation | OpenAI GPT-4o |
| AI â€” refinement | Anthropic Claude Sonnet |
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
     â†“
Job 1: Frontend â€” npm ci + tsc + vite build
Job 2: Backend  â€” pip install + ruff lint + mypy type check
     â†“ (both must pass)
Job 3: Docker   â€” build image + push to Artifact Registry
     â†“
Job 4: Deploy   â€” Google Cloud Run auto-deployment
```

---

## Key engineering decisions

**Why two AI models?**
GPT-4o handles creative generation. Claude handles tone refinement and platform formatting. Each model does what it's better at â€” specialisation, not redundancy.

**Why asyncio.gather for platform formatting?**
Platform jobs are independent. Running them concurrently reduces formatting time from O(n) to roughly O(1).

**Why the pipeline is isolated in orchestrator/pipeline.py**
The pipeline is completely separated from the HTTP layer. It can be triggered from a route, background job, or n8n webhook without any code changes.

**Retry logic**
Every API call uses exponential backoff (2^attempt seconds). Rate limits and API errors are caught separately. After max retries the error propagates cleanly as a 502.

**Prompt versioning**
Tone instructions live in config objects â€” brand voice updates are one-line changes, not code changes.

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

**Frontend â†’ Vercel**
```bash
cd frontend && vercel
```

**Backend â†’ Google Cloud Run**
```bash
gcloud run deploy scriptforge-api --source ./backend --region us-east1 --allow-unauthenticated
```

Or push to main â€” the GitHub Actions pipeline deploys automatically.

---

## Environment variables

**Backend `.env`**
```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
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
