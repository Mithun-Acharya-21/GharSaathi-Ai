# GharSaathi Maths — Backend

FastAPI backend service for **GharSaathi Maths**, a multilingual home-learning
mathematics application for Grades 1–6. It exposes the REST API for anonymous
parent/child sessions, speech transcription (Gnani Prisma STT), optional spoken
instructions (Gnani Timbre TTS), deterministic answer evaluation, and teacher
reporting.

## Stack

- Python 3.12, FastAPI, Pydantic v2 / pydantic-settings
- SQLAlchemy 2.x (async) + asyncpg + Alembic, PostgreSQL 16
- HTTPX async client for Gnani STT/TTS integrations
- pytest + pytest-asyncio, Ruff, Docker Compose

## Setup (local)

```bash
cp ../.env.example .env        # set DB and GNANI_* credentials
uv pip install -e ".[dev]"     # or: pip install -e ".[dev]"
alembic upgrade head           # apply database migrations
python scripts/seed_activities.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive API docs: <http://localhost:8000/docs>

## Tests & lint

```bash
pytest -v
ruff check .
```

## Docker

From the repository root:

```bash
docker compose up -d --build   # PostgreSQL + API
docker compose logs -f api
```

The image installs this package with `pip install .` using Hatchling, so
`pyproject.toml` and this `README.md` must be present in the build context
(`./backend`) — the Dockerfile copies them before running the install.

See the root `README.md` for the full architecture, API contract, and privacy
policy.
