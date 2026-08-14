# Parakh — AI Truth Verification Platform

> **Before you believe it. Verify it.**

Parakh is a browser-based implementation of **"The Truth Agent"** — an AI system that
verifies suspicious claims (text, screenshots, articles, or voice) against reliable
evidence instead of trusting a language model's own "knowledge." It's built so the
same verification engine can power a WhatsApp bot later with zero changes to the core.

```
Input → Extract Claim → Check Ledger → Retrieve Evidence → Verify → Explain → Save to Ledger
```

## Why it's trustworthy by design

- **The LLM never invents evidence.** Verification is only ever judged against
  evidence snippets retrieved from a search provider — if there's no evidence, the
  verdict is `UNVERIFIED`, full stop.
- **Reliability is a fixed lookup table**, not an LLM opinion (`backend/app/core/source_reliability.py`).
  A random blog can never outrank PIB, WHO, or Reuters.
- **No confidence percentages.** Every result reports **Evidence Strength: LOW / MEDIUM / HIGH**,
  a signal grounded in *how many reliable sources* corroborate it — not a made-up number.
- **Every AI output is schema-validated** before it touches the database (`backend/app/utils/validation.py`).
  An invalid verdict from the model degrades to `UNVERIFIED`, never a silent bad write.
- **Everything has an offline fallback.** No API keys? Parakh still runs, end to end,
  with deterministic rule-based providers — see [Provider fallbacks](#provider-fallbacks).

## Features

| Feature | Where |
|---|---|
| 📝 Text verification | Home → Text tab |
| 📷 Image / screenshot OCR verification | Home → Image tab |
| 🔗 News/article URL verification | Home → URL tab |
| 🎙️ Voice input (English + Hindi), spoken explanation | Home → Voice tab |
| 🟢🔴🟡⚪ Four verdicts: Verified / False / Misleading / Unverified | Result card |
| 📤 Share a result back to WhatsApp/social (native share sheet, WhatsApp deep link, or copy) | Result card → Share |
| 💬 Real WhatsApp bot — text a claim or forward a screenshot, get a fact-check reply | Twilio webhook, `/api/webhooks/whatsapp` |
| Persistent, semantically-deduped verification ledger | `claims` table + dashboard |
| Public dashboard: totals, categories, most-checked, recent, search | `/dashboard` |

## Architecture

```
                 ┌──────────────────────────┐
   Browser  ───▶ │   Truth Agent API         │   (FastAPI, transport-agnostic core)
 (React/Vite)    │                           │
                 │  extract_claim()          │──▶ LLM provider   (Anthropic | mock)
                 │  find_similar_claim()     │──▶ Embedding provider (sentence-transformers | hashing)
                 │  retrieve_evidence()      │──▶ Search provider (Tavily | mock)
                 │  verify_claim()           │──▶ LLM provider, evidence-only
                 │  save to ledger           │──▶ MySQL / SQLite via SQLAlchemy
                 └──────────────────────────┘
```

`backend/app/core/pipeline.py` is the entire loop in one transport-agnostic function.
The WhatsApp webhook (`backend/app/routers/whatsapp.py`) calls
`run_verification_pipeline(db, message_text, InputType.TEXT)` — the exact same call
the `/api/verify/text` route makes — **proving** the "no core logic changes to add
a channel" claim rather than just asserting it.

## Tech stack

- **Frontend:** React + TypeScript + Vite + Tailwind CSS, React Router, Recharts, Web Speech API
- **Backend:** Python + FastAPI
- **Database:** MySQL or Postgres (or SQLite for zero-setup local dev) + SQLAlchemy
- **AI:** Anthropic Claude or Groq (structured tool-use JSON output), with a fully offline mock fallback
- **OCR:** Tesseract (via `pytesseract`)
- **Voice:** Browser-native Web Speech API (STT + TTS) — no API key, works offline in-browser
- **Semantic search:** `sentence-transformers` embeddings + cosine similarity, with a
  zero-dependency hashing fallback

## Project layout

```
backend/
  app/
    core/          # pipeline, OCR, URL extraction, semantic matching, reliability rules
    providers/      # llm/ search/ embeddings/ — each with a real + mock implementation
    routers/        # verify.py, ledger.py, dashboard.py
    models.py       # SQLAlchemy tables: claims, evidence_items, verification_history
    schemas.py       # Pydantic request/response contracts
  scripts/seed_demo_data.py
  requirements.txt
  .env.example
frontend/
  src/
    pages/          # HomePage, DashboardPage
    components/      # ResultCard, VerdictBadge, panels/ (Text/Image/Url/Voice), charts…
    hooks/useSpeech.ts
    api/client.ts
  .env.example
database/
  schema.sql        # reference schema (backend also auto-creates this via SQLAlchemy)
```

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- MySQL 8 (optional — SQLite works out of the box for local dev)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (optional — only needed for the Image tab;
  on Windows: `winget install --id UB-Mannheim.TesseractOCR -e`)

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
copy .env.example .env       # cp .env.example .env  (macOS/Linux)
```

Edit `backend/.env` as needed (every field has a working default — see
[Environment variables](#environment-variables)). Then:

```bash
# optional: populate the dashboard with sample data
python -m scripts.seed_demo_data

uvicorn app.main:app --reload --port 8000
```

Check it's alive: `curl http://127.0.0.1:8000/api/health`

### 2. Frontend

```bash
cd frontend
npm install
copy .env.example .env       # cp .env.example .env  (macOS/Linux) — defaults are fine
npm run dev
```

Open **http://localhost:5173**. Vite proxies `/api` to `http://127.0.0.1:8000` automatically
(see `frontend/vite.config.ts`) — no CORS setup needed in dev.

### 3. MySQL (optional, for production-like setup)

```bash
mysql -u root -p < database/schema.sql
```

Then in `backend/.env`:
```
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/parakh
```
(The backend also creates these tables automatically on startup if they don't exist —
`database/schema.sql` is there for reference/manual provisioning.)

## Environment variables

Every provider below defaults to a fully-functional **offline/mock mode**. Add API keys
to unlock the real ones — nothing needs to change in code.

**`backend/.env`** (see `backend/.env.example` for the full annotated file):

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./parakh.db` | Swap for `mysql+pymysql://...` (MySQL) or `postgresql://...` (Postgres, e.g. Render's managed DB) |
| `LLM_PROVIDER` | `mock` | `anthropic`, `groq`, or `mock` — see below |
| `ANTHROPIC_API_KEY` | _(empty)_ | Required if `LLM_PROVIDER=anthropic` |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | |
| `GROQ_API_KEY` | _(empty)_ | Required if `LLM_PROVIDER=groq`. Get one free at [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Fast, low-cost reasoning via Groq's OpenAI-compatible tool-calling API |
| `SEARCH_PROVIDER` | `mock` | `tavily` enables live web evidence search |
| `TAVILY_API_KEY` | _(empty)_ | Get one at [tavily.com](https://tavily.com) |
| `EMBEDDING_PROVIDER` | `sentence_transformer` | Falls back to `hashing` automatically if torch isn't installed |
| `SIMILARITY_THRESHOLD` | `0.85` | Cosine similarity above which two claims are treated as the same |
| `TESSERACT_CMD` | _(empty)_ | Set to the full path on Windows if Tesseract isn't on PATH |

**`frontend/.env`**: `VITE_API_BASE_URL` — leave empty for local dev (Vite proxy handles it).

## Provider fallbacks

Parakh is built API-first with an abstraction layer over every external dependency
(`backend/app/providers/`), each with a real and a mock implementation, selected
automatically by `backend/app/providers/factory.py`:

| Layer | Real | Offline fallback |
|---|---|---|
| Reasoning | Anthropic Claude or Groq (Llama 3.3 70B), both forced tool-use JSON | Regex-based claim cleaning + keyword-overlap verdict scoring |
| Evidence search | Tavily web search | Curated, clearly-labeled `[Demo]` evidence set covering well-known fact-checked myths |
| Semantic similarity | `sentence-transformers` (MiniLM) | Deterministic hashed bag-of-words vectors |

The mock modes are **not stubs** — they're deterministic and fully wired so the whole
loop (extract → dedupe → retrieve → verify → explain → persist) works with zero API keys.
Run `python -m scripts.seed_demo_data` to see it in action immediately.

**Trade-off to know:** the hashing embedding fallback catches near-duplicate reworded
claims well, but true paraphrase detection (e.g. "₹50,000 to engineering students" vs.
"50k from the government") is noticeably stronger with real `sentence-transformers`
embeddings — that's the intended default.

## API reference

All endpoints are transport-agnostic — a WhatsApp integration would call the same ones.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/verify/text` | `{ text }` → `ClaimResult` |
| `POST` | `/api/verify/voice` | `{ text, language }` → `ClaimResult` (text is browser-transcribed speech) |
| `POST` | `/api/verify/image` | multipart `file` → OCR → `ClaimResult` |
| `POST` | `/api/verify/url` | `{ url }` → article extraction → `ClaimResult` |
| `GET` | `/api/ledger` | `?search=&verdict=&category=&page=&page_size=` → paginated ledger |
| `GET` | `/api/ledger/{id}` | Full detail for one claim |
| `GET` | `/api/dashboard/stats` | Totals, category breakdown, most-checked, recent |
| `GET` | `/api/health` | Liveness + active provider config |
| `POST` | `/api/webhooks/whatsapp` | Twilio incoming-message webhook → same pipeline → TwiML reply |

Interactive docs: `http://127.0.0.1:8000/docs` (FastAPI's built-in Swagger UI).

## Database schema

See [`database/schema.sql`](database/schema.sql). Three tables:

- **`claims`** — the ledger itself: original + normalized text, verdict, evidence
  strength, explanation, category, embedding vector, `check_count`, timestamps.
- **`evidence_items`** — sources attached to a claim, with computed reliability tier.
- **`verification_history`** — every raw submission, including ones that matched an
  existing ledger entry (this is where `check_count` comes from).

## Connecting WhatsApp (Twilio Sandbox)

The WhatsApp channel is implemented — `backend/app/routers/whatsapp.py` — not just
architected for. It receives Twilio's incoming-message webhook, verifies Twilio's
signature, calls the exact same `run_verification_pipeline()` the browser uses, and
replies with a plain-text summary via TwiML. Text messages and forwarded screenshots
(via the existing OCR pipeline) both work; a bare "hi" gets a short help reply instead
of being sent through verification.

### Setup

1. **Twilio account** → console.twilio.com (free trial, no card required to start).
2. **Open the WhatsApp Sandbox**: Console → Messaging → Try it out → Send a WhatsApp
   message. You'll get a shared sandbox number and a join code like `join purple-tiger`.
3. **Join it** by sending that join code as a WhatsApp message, from your own phone,
   to the sandbox number.
4. **Get a public URL for your backend**:
   - Already deployed on Render? Use that URL directly — see [Deployment](#deployment).
   - Testing locally? Run `ngrok http 8000` and use the `https://...ngrok-free.app` URL it gives you.
5. **Configure the sandbox webhook**: in the Sandbox settings, set "WHEN A MESSAGE COMES IN"
   to `https://<your-public-url>/api/webhooks/whatsapp`, method `POST`.
6. **Set env vars** (`backend/.env` locally, or the Render dashboard if deployed):
   ```
   TWILIO_ACCOUNT_SID=AC...       # Console → Account Info
   TWILIO_AUTH_TOKEN=...          # Console → Account Info
   PUBLIC_BASE_URL=https://<your-public-url>   # must match step 5 exactly
   ```
7. Restart the backend (or redeploy). Send a WhatsApp message to the sandbox number —
   you should get a fact-check reply within a few seconds.

`TWILIO_AUTH_TOKEN`/`PUBLIC_BASE_URL` left blank means the webhook still runs but
skips signature verification (logs a warning) — useful for testing the route with a
raw `curl` request, but don't leave it that way once real Twilio credentials are set,
since that's what stops anyone else from posting fake messages to your webhook.

The sandbox is meant for development: anyone testing it also has to send the join
code first, and Twilio's real production WhatsApp approval (a Meta Business
verification process) takes days, not minutes — fine for a hackathon demo video,
not for a public launch.

## Deployment

Frontend and backend deploy to different hosts — Vercel is a poor fit for the
backend (ephemeral filesystem, no room for the Tesseract system binary, short
execution limits), so the split here is: **Vercel for the frontend, Render for
the backend + database.**

### Backend → Render

1. Push this repo to GitHub (Render deploys from a git repo).
2. In the Render dashboard: **New +** → **Blueprint** → point at the repo.
   Render reads [`render.yaml`](render.yaml) at the repo root and creates:
   - `parakh-backend` — a Docker web service built from `backend/Dockerfile`
     (Tesseract OCR baked in, lean dependency set — see
     `backend/requirements-deploy.txt`)
   - `parakh-db` — a free managed Postgres database, wired to the service via
     `DATABASE_URL` automatically
3. In the service's **Environment** tab, fill in the secrets `render.yaml`
   leaves blank (`sync: false`): `GROQ_API_KEY`, `TAVILY_API_KEY`, and
   `CORS_ORIGINS` (leave `CORS_ORIGINS` for step 5, once you have the Vercel URL).
4. Deploy. Confirm it's alive: `curl https://<your-service>.onrender.com/api/health`
5. Seed demo data against the deployed backend (optional): a Render **Shell**
   session (or a one-off Job) running `python -m scripts.seed_demo_data`.

Note: Render's free tier spins the service down after inactivity — the first
request after idling takes ~30-50s to cold-start. Fine for a demo video with a
few seconds of patience on the first request; not fine for a live, no-warning demo.

### Frontend → Vercel

1. **New Project** in Vercel → import the same repo.
2. Set **Root Directory** to `frontend` (this is a monorepo — Vercel needs to
   know where the frontend actually lives).
3. Vercel auto-detects Vite via `frontend/vercel.json` (build command, output
   directory, and SPA rewrite are already configured there).
4. Add an environment variable: `VITE_API_BASE_URL` = your Render backend URL
   (e.g. `https://parakh-backend.onrender.com`) — this replaces the dev-only
   Vite proxy, which doesn't exist in a production build.
5. Deploy. Once you have the Vercel URL, go back to Render and set
   `CORS_ORIGINS` to it (e.g. `https://parakh.vercel.app`), so the browser is
   actually allowed to call the API cross-origin. Redeploy the backend for it
   to take effect.

### WhatsApp webhook, once deployed

A deployed Render backend already has a stable public URL, which is exactly what the
Twilio webhook needs — no `ngrok` tunnel required. Set the Sandbox's webhook to
`https://<your-service>.onrender.com/api/webhooks/whatsapp`, and set that same URL as
`PUBLIC_BASE_URL` in the Render dashboard. Full steps: [Connecting WhatsApp](#connecting-whatsapp-twilio-sandbox).

## Known limitations (by design, not oversight)

- Mock LLM/search modes are heuristic, not a substitute for the real Claude + Tavily
  pipeline — they exist so the app is demoable with zero setup, not as a production
  reasoning engine.
- OCR requires the Tesseract binary installed separately (it's a system dependency,
  not a Python package) — the Image tab returns a clear setup error if it's missing.
- Voice uses the browser's built-in Web Speech API (Chrome/Edge have the best support);
  there's no server-side speech fallback in this version.
