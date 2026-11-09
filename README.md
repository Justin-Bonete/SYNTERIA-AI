# SYNTRA AI — Phase 1: Foundation

A self-hosted personal AI assistant. This phase delivers the base everything else sits on:
backend API, database, owner login, audit log, and a dashboard shell.

## What works in Phase 1
- FastAPI backend with `/api/v1/health` and `/api/v1/auth/{register,login,me}`
- Passwords hashed with bcrypt, JWT sessions
- **Single-owner mode:** the first account becomes the owner; registration then closes
- Audit log table recording registrations and login successes/failures
- Dashboard page (login, health status, placeholders for upcoming features)
- PostgreSQL + pgvector ready for Phase 3 (embeddings)

## Option A — Run on your laptop without Docker (lightest)
Requires Python 3.11+.

    cd backend
    python -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    cp ../.env.example .env          # then edit SECRET_KEY
    uvicorn app.main:app --reload

Open http://127.0.0.1:8000 and create the owner account. Uses a local SQLite file.

## Option B — Docker (PostgreSQL + pgvector)
    cp .env.example .env             # edit DB_PASSWORD and SECRET_KEY
    docker compose up --build

Open http://127.0.0.1:8000.

## Run the tests
    cd backend
    pytest

## Phase 1 acceptance checklist
- [ ] `pytest` passes
- [ ] Owner account can be created and can sign in
- [ ] A second registration is rejected
- [ ] Wrong password is rejected and logged in `audit_logs`
- [ ] Dashboard shows "Backend online"

## Roadmap
2. Chat + model gateway (hosted model first, local Ollama later via the same adapter)
3. Memory + document knowledge (RAG)
4. Agents + tool gateway
5. Approvals, audit, sandboxing
6. Voice and vision
7. Workflows and integrations
8. Hardening, testing, release
