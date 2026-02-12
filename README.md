# Risko.ai

AI-powered platform for discovering viral trends, analyzing short-form videos, and generating content scripts using multiple AI models.

## Features

- **Trend Discovery** — Search and analyze trending TikTok/Instagram/YouTube videos with UTS (Universal Trend Score)
- **AI Chat** — Multi-model chat assistant (Gemini, Claude, GPT-4) for content strategy
- **Video Analysis** — Native video analysis via Gemini 2.0 — AI watches the actual video, not just metadata
- **Workflow Builder** — Visual drag-and-drop pipeline: Video → Analyze → Generate → Script
- **AI Script Generator** — Generate viral scripts with hooks, body, CTA, and pro tips
- **Credit System** — Per-model billing with monthly allocations by subscription tier
- **OAuth** — Google and GitHub login via Supabase

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite 7, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, SQLAlchemy 2.0, Alembic |
| Database | PostgreSQL 15 + pgvector (Supabase) |
| Auth | JWT + Supabase OAuth (Google, GitHub) |
| AI Models | Google Gemini 2.0 Flash, Anthropic Claude, OpenAI GPT-4 |
| Video Download | yt-dlp (TikTok, Instagram, YouTube Shorts) |
| Data Source | Apify API (trend scraping) |

## Quick Start

### Prerequisites

- **Node.js** 18+ ([download](https://nodejs.org/))
- **Python** 3.11+ ([download](https://www.python.org/downloads/))
- **PostgreSQL** 15+ — recommended via [Supabase](https://supabase.com/) (free tier)
- **Git** ([download](https://git-scm.com/))

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/risko-ai.git
cd risko-ai
```

### 2. Setup environment variables

```bash
# Root .env (used by both server and client)
cp server/.env.example server/.env
cp client/.env.example client/.env
```

Edit the `.env` files with your actual keys. See [Environment Variables](#environment-variables) below.

### 3. Setup Backend

```bash
cd server

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Additional packages for full functionality
pip install anthropic openai python-dateutil yt-dlp

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`
API docs (Swagger): `http://localhost:8000/docs`

### 4. Setup Frontend

```bash
cd client

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## Environment Variables

Create a `.env` file in the project root (or in `server/` directory):

| Variable | Required | Description | Where to get |
|----------|----------|-------------|--------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string | [Supabase](https://supabase.com/) → Project Settings → Database |
| `SECRET_KEY` | Yes | JWT signing key | Any random string (32+ chars) |
| `GEMINI_API_KEY` | Yes | Google Gemini API key | [Google AI Studio](https://aistudio.google.com/apikey) |
| `APIFY_API_TOKEN` | Yes | Apify scraping token | [Apify Console](https://console.apify.com/) |
| `ANTHROPIC_API_KEY` | Optional | Claude API key | [Anthropic Console](https://console.anthropic.com/) |
| `OPENAI_API_KEY` | Optional | GPT-4 API key | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `GOOGLE_CLIENT_ID` | Optional | Google OAuth client ID | [Google Cloud Console](https://console.cloud.google.com/) |
| `GOOGLE_CLIENT_SECRET` | Optional | Google OAuth secret | Same as above |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | JWT token lifetime (default: 30) | — |

**Client `.env`** (in `client/` directory):

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes | Backend API URL, e.g. `http://localhost:8000/api` |
| `VITE_GOOGLE_CLIENT_ID` | Optional | Same Google OAuth client ID |

## Database Setup

### Option A: Supabase (recommended)

1. Create a free project at [supabase.com](https://supabase.com/)
2. Go to **Project Settings → Database** and copy the connection string
3. Enable pgvector: run `CREATE EXTENSION IF NOT EXISTS vector;` in SQL Editor
4. Set `DATABASE_URL` in your `.env`
5. Run `alembic upgrade head` to create all tables

### Option B: Local PostgreSQL

```bash
createdb risko_ai
psql risko_ai -c "CREATE EXTENSION IF NOT EXISTS vector;"
# Set DATABASE_URL=postgresql://user:password@localhost:5432/risko_ai
alembic upgrade head
```

## Project Structure

```
risko-ai/
├── client/                    # React frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   │   ├── ui/            # shadcn/ui primitives
│   │   │   └── workflow/      # Workflow builder components
│   │   ├── contexts/          # React contexts (Chat, Workflow, Auth)
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client
│   │   └── types/             # TypeScript types
│   └── package.json
├── server/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   ├── chat_sessions.py    # AI chat endpoints
│   │   │   ├── workflows.py        # Workflow CRUD + execution
│   │   │   ├── dependencies.py     # Auth, credits, rate limiting
│   │   │   └── routes/             # Auth, videos, scripts
│   │   ├── db/
│   │   │   ├── models.py           # SQLAlchemy models
│   │   │   ├── database.py         # DB connection
│   │   │   └── migrations/         # Alembic migrations
│   │   ├── services/               # Business logic
│   │   │   ├── video_analyzer.py   # Video download + Gemini analysis
│   │   │   └── workflow_templates.py
│   │   └── main.py
│   └── requirements.txt
├── ml-service/                # ML microservice (optional)
├── schema.sql                 # Full DB schema reference
├── docker-compose.yml         # Docker setup
└── .env                       # Environment variables (not in git)
```

## Credit System

Each subscription tier gets monthly credits:

| Plan | Credits/Month | Price |
|------|--------------|-------|
| Free | 100 | $0 |
| Creator | 1,000 | — |
| Pro | 5,000 | — |
| Agency | 10,000 | — |

AI model costs per message:

| Model | Credits |
|-------|---------|
| Gemini 2.0 Flash | 1 |
| GPT-4 | 4 |
| Claude | 5 |

## API Endpoints

### Auth
- `POST /api/auth/register` — Register new user
- `POST /api/auth/login` — Login (returns JWT)
- `POST /api/auth/oauth/sync` — Sync OAuth login

### Chat
- `POST /api/chat/sessions` — Create chat session
- `GET /api/chat/sessions` — List sessions
- `POST /api/chat/sessions/{id}/messages` — Send message (supports model selection)

### Workflows
- `GET /api/workflows/` — List workflows
- `POST /api/workflows/` — Create workflow
- `PATCH /api/workflows/{id}` — Update workflow
- `POST /api/workflows/execute` — Run workflow pipeline
- `GET /api/workflows/templates/list` — Get pre-built templates

### Videos
- `GET /api/videos/trending` — Search trending videos
- `POST /api/videos/favorites` — Save to favorites
- `POST /api/workflows/analyze-video` — Analyze video with Gemini

## Development

```bash
# Run backend (with auto-reload)
cd server && uvicorn app.main:app --reload --port 8000

# Run frontend (with HMR)
cd client && npm run dev

# Build frontend for production
cd client && npm run build

# Run database migrations
cd server && alembic upgrade head

# Create new migration
cd server && alembic revision --autogenerate -m "description"
```

## License

MIT
