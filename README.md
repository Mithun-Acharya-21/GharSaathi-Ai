# GharSaathi Maths — Complete FastAPI Backend

> **Multilingual Home-Learning Mathematics Application for Grades 1–6**

GharSaathi Maths empowers parents to guide and support their children through interactive mathematics activities using everyday household items. It combines voice input transcribed through **Gnani Prisma v2.5 STT**, optional spoken instructions via **Gnani Timbre TTS**, human-in-the-loop parent transcript confirmation, deterministic pedagogical evaluation, and child-safe privacy controls.

---

## Architecture Highlights

- **Modular Monolith**: Clean separation across API, Service, Domain, Repository, and Integration layers.
- **FastAPI + Async Python 3.12**: Non-blocking I/O throughout, using HTTPX AsyncClient and SQLAlchemy 2.x with asyncpg.
- **Genuine AI Integration**: Direct integration with official Gnani Vachana AI endpoints (`stt/v3` and `tts/inference`).
- **Deterministic Mathematics Evaluator**: Zero hallucination risk—evaluates answers against strict server-side specifications using Python `Decimal` and multilingual normalization (Kannada digits `೧೨`, Devanagari `१२`, words, and symbols).
- **Child Privacy Safeguards**: Zero PII collected (no names, dates of birth, emails, phone numbers, or school IDs). Raw audio is kept strictly in-memory and deleted immediately after transcription. High-entropy random session bearer tokens are hashed with SHA-256 before database storage.
- **Parent-in-the-Loop**: A draft speech transcript is always reviewed and confirmed by a parent before evaluation.

---

## Technology Stack

- **Python 3.12+**
- **FastAPI 0.115+**
- **SQLAlchemy 2.x Async ORM** + **asyncpg** + **Alembic**
- **PostgreSQL 16/18**
- **Pydantic v2** & **Pydantic Settings**
- **HTTPX AsyncClient**
- **python-multipart**
- **pytest** + **pytest-asyncio**
- **Ruff** (Linter & Formatter)
- **Docker Compose**

---

## Project Structure

```
backend/
    pyproject.toml                # Project metadata and dependencies
    Dockerfile                    # Production Dockerfile
    alembic.ini                   # Alembic migration configuration
    app/
        main.py                   # FastAPI application factory, middleware, lifespan
        core/
            config.py             # Typed Pydantic Settings
            lifespan.py           # Shared HTTPX client and DB shutdown
            logging.py            # Sanitized logging setup
            errors.py             # Custom application exceptions and global handlers
            security.py           # Token generation, SHA-256 hashing, constant-time validation
        api/
            router.py             # Combines all /api/v1 routes
            dependencies.py       # Dependency injection (Auth, DB, Services, Providers)
            routes/
                health.py         # /healthz and /readyz
                activities.py     # /api/v1/grades, /api/v1/activities
                sessions.py       # /api/v1/sessions
                attempts.py       # /transcribe, /text, /confirm, /evaluate
                speech.py         # /api/v1/speech/synthesize
                teacher.py        # /api/v1/teacher/reports, /api/v1/teacher/review-queue
        schemas/
            common.py             # Standard base schemas and error format
            activity.py           # Public activity schemas (evaluator config omitted)
            session.py            # Session creation and detail schemas
            attempt.py            # Transcription, text fallback, confirmation, evaluation
            speech.py             # TTS speech synthesis schemas
            teacher.py            # Teacher aggregate reporting and review queue
        domain/
            enums.py              # StrEnum definitions (QuestionType, SessionStatus, etc.)
            evaluation.py         # Deterministic mathematical evaluation engine
            state_transitions.py  # Explicit state transition validations
        models/
            base.py               # DeclarativeBase, UTC helpers, UUID generator
            activity.py           # Activities table
            session.py            # Sessions table
            attempt.py            # Attempts table
        repositories/
            activity_repository.py
            session_repository.py
            attempt_repository.py
            teacher_repository.py
        services/
            activity_service.py
            session_service.py
            attempt_service.py
            teacher_service.py
        integrations/
            gnani_prisma.py       # Gnani Prisma STT v3 adapter
            gnani_timbre.py       # Gnani Timbre TTS adapter
        db/
            session.py            # Async engine and sessionmaker
        seed/
            activities.py         # Deterministic starter activities for Grades 1–6
    migrations/
        env.py                    # Async migration environment
        versions/
            001_initial_schema.py # Initial database schema
    tests/
        unit/                     # Evaluation, transitions, security, adapter tests
        api/                      # Full API lifecycle tests
        integration/              # Database seeding idempotency and retention tests
        conftest.py               # Fixtures, test DB, and mock clients
    scripts/
        seed_activities.py        # Standalone idempotent seeding script
        purge_expired_sessions.py # Retention cleanup script
docker-compose.yml                # Multi-container setup (PostgreSQL + FastAPI)
.env.example                      # Configuration template
Makefile                          # Developer task runner
docs/
    architecture.md               # Architecture specification and data flows
    api-contract.md               # Exhaustive REST API contract with examples
    verification-report.md        # Complete verification report and test summary
```

---

## Quickstart

### Option 1: Local Development with `uv`

1. **Install dependencies**:
   ```bash
   cd backend
   uv venv --python 3.12 .venv
   uv pip install -e ".[dev]"
   ```

2. **Configure environment variables**:
   ```bash
   cp ../.env.example .env
   # Edit .env with your PostgreSQL credentials and GNANI_API_KEY
   ```

3. **Run database migrations**:
   ```bash
   uv run alembic upgrade head
   ```

4. **Seed Grade 1–6 mathematics activities**:
   ```bash
   uv run python scripts/seed_activities.py
   ```

5. **Start FastAPI development server**:
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Open interactive documentation at: [http://localhost:8000/docs](http://localhost:8000/docs)

6. **Run test suite**:
   ```bash
   uv run pytest -v
   ```

7. **Run linter and formatter**:
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   ```

---

### Option 2: Docker Compose

Start PostgreSQL and FastAPI with a single command:
```bash
docker compose up -d --build
```
This automatically initializes PostgreSQL, executes database migrations, seeds the 6 activities, and starts the FastAPI service at `http://localhost:8000`.

To inspect logs:
```bash
docker compose logs -f api
```

To shut down:
```bash
docker compose down
```

---

## Core Product Flow & API Usage

### Step 1: Browse Activities
Parent selects a grade (e.g. Grade 3 Multiplication):
```http
GET /api/v1/activities?grade=3&language_code=kn-IN
```

### Step 2: Start an Anonymous Session
Parent starts the session and provides guardian consent:
```http
POST /api/v1/sessions
Content-Type: application/json

{
  "activity_id": "a3000000-0000-0000-0000-000000000003",
  "language_code": "kn-IN",
  "consent_acknowledged": true
}
```
**Response**:
```json
{
  "session_id": "67245d8b-5777-4467-b505-1815f917574a",
  "session_token": "u4J59fGZ9e7kH13vQ..."
}
```
> **Important**: Save `session_token` securely on the client. It must be passed on all subsequent requests:
> `Authorization: Bearer <session_token>`

### Step 3 (Optional): Spoken Parent Instructions
Listen to teacher-reviewed activity instructions in Kannada via Gnani Timbre:
```http
POST /api/v1/speech/synthesize
Content-Type: application/json

{
  "activity_id": "a3000000-0000-0000-0000-000000000003",
  "text_type": "instructions",
  "language_code": "kn-IN"
}
```
Returns binary `audio/wav`.

### Step 4: Submit Child's Spoken Answer
Send audio recording for real-time transcription via Gnani Prisma v2.5:
```http
POST /api/v1/sessions/67245d8b-5777-4467-b505-1815f917574a/attempts/transcribe
Authorization: Bearer <session_token>
Content-Type: multipart/form-data

audio_file=@child_audio.wav
```
**Response**:
```json
{
  "attempt_id": "4b68eef0-4822-4a0b-8d82-8407fc29418a",
  "transcription_status": "completed",
  "evaluation_status": "pending_confirmation",
  "transcript": "12",
  "provider": "gnani-prisma-v2.5"
}
```

*(Or use typed answer fallback if microphone is unavailable):*
```http
POST /api/v1/sessions/67245d8b-5777-4467-b505-1815f917574a/attempts/text
Authorization: Bearer <session_token>
Content-Type: application/json

{
  "answer": "12"
}
```

### Step 5: Review and Confirm Answer
Parent reviews the transcript on screen and confirms the child's final answer:
```http
PATCH /api/v1/attempts/4b68eef0-4822-4a0b-8d82-8407fc29418a/confirm
Authorization: Bearer <session_token>
Content-Type: application/json

{
  "confirmed_answer": "12",
  "corrected_transcript": "12"
}
```

### Step 6: Evaluate Confirmed Answer
Evaluate the answer deterministically against the server-side specification:
```http
POST /api/v1/attempts/4b68eef0-4822-4a0b-8d82-8407fc29418a/evaluate
Authorization: Bearer <session_token>
```
**Response**:
```json
{
  "attempt_id": "4b68eef0-4822-4a0b-8d82-8407fc29418a",
  "evaluation_status": "evaluated",
  "is_correct": true,
  "feedback": "ತುಂಬಾ ಒಳ್ಳೆಯದು! 3 ಬಾರಿ 4 ಅಂದರೆ 3 × 4 = 12. ಸಮಾನ ಗುಂಪುಗಳನ್ನು ನೀವು ಸರಿಯಾಗಿ ಅರ್ಥೈಸಿಕೊಂಡಿದ್ದೀರಿ!",
  "next_hint": null,
  "review_required": false
}
```

### Step 7: Teacher Review & Reporting
Teachers can inspect aggregate learning metrics without student identities:
```http
GET /api/v1/teacher/reports?grade=3
X-Teacher-API-Key: <teacher_key>
```
Inspect cases needing pedagogical review:
```http
GET /api/v1/teacher/review-queue?grade=3
X-Teacher-API-Key: <teacher_key>
```

---

## Data Privacy & Retention Policy

1. **Zero Permanent Audio**: Raw audio files are processed in-memory during transcription and immediately discarded.
2. **Session Token Security**: Only SHA-256 cryptographic hashes of bearer tokens are stored in the database.
3. **Automated Session Cleanup**:
   Run the purge command to delete sessions older than `DATA_RETENTION_DAYS` (default 30 days):
   ```bash
   uv run python scripts/purge_expired_sessions.py
   ```
4. **Immediate Deletion**: A parent can delete their session and all associated attempts at any time via `DELETE /api/v1/sessions/{session_id}`.
