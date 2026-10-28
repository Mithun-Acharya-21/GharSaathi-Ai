# GharSaathi Maths — Backend Architecture

## 1. System Overview

GharSaathi Maths is a multilingual home-learning mathematics application for Grades 1–6 designed to support parents and children learning together.

The backend is built as a clean **FastAPI Modular Monolith** adhering to strict layering:
- **Presentation Layer (API)**: FastAPI routers, request validation, response serialization, route-level security dependencies.
- **Service Layer**: Business logic, workflow coordination, orchestration of domain logic and external integrations.
- **Domain Layer**: Pure business logic, state machines, mathematics evaluation engine, domain enums and invariants (no HTTP or database dependencies).
- **Data Access Layer (Repositories & Models)**: SQLAlchemy 2.x asynchronous ORM, asyncpg driver, typed repository queries, Alembic migrations.
- **External Integration Layer**: Gnani Prisma (STT) and Gnani Timbre (TTS) asynchronous HTTP adapters using shared HTTPX AsyncClient with graceful timeouts and sanitized error mapping.

## 2. High-Level Architecture Diagram

```
                 +---------------------------------------------+
                 |          Frontend (Parent & Child)          |
                 +---------------------------------------------+
                        | (Bearer Session Token / Multipart Audio)
                        v
                 +---------------------------------------------+
                 |            FastAPI Application              |
                 |     Global Middleware, Lifespan, Errors     |
                 +---------------------------------------------+
                   |                 |                 |
                   v                 v                 v
           +---------------+ +---------------+ +---------------+
           | /api/v1/      | | /api/v1/      | | /api/v1/      |
           | activities,   | | transcribe,   | | teacher/      |
           | sessions      | | evaluate      | | reports       |
           +---------------+ +---------------+ +---------------+
                   |                 |                 |
                   +--------+--------+--------+--------+
                            |                 |
                            v                 v
                    +---------------+ +---------------+
                    |    Service    | |    Domain     |
                    |     Layer     | |  Evaluation   |
                    +---------------+ +---------------+
                      |           |           |
                      v           |           v
            +-------------------+ |  +--------------------+
            |   Repositories    | |  |    Integrations    |
            |   (SQLAlchemy)    | |  | (Prisma / Timbre)  |
            +-------------------+ |  +--------------------+
                      |           |           |
                      v           v           v
            +-------------------+     +--------------------+
            | PostgreSQL 16/18  |     |  Gnani Vachana AI  |
            | (Async asyncpg)   |     |   Cloud Services   |
            +-------------------+     +--------------------+
```

## 3. Core Workflow

1. **Grade Selection & Activity Discovery**:
   - Parent browses activities filtered by `grade` (1-6) and `language_code` (`kn-IN`, `en-IN`, etc.).
   - Activity schema exposes instructions, prompts, materials, and hints, keeping `evaluator_config` strictly confidential.

2. **Session Initialization & Guardian Consent**:
   - Parent initiates a session for an activity, acknowledging guardian consent.
   - Server generates a cryptographically secure random session bearer token (`secrets.token_urlsafe(32)`), stores its SHA-256 hash in PostgreSQL, and returns the raw token once.

3. **Spoken Instruction Playback (Timbre TTS)**:
   - Optional server-side speech synthesis of approved activity instructions via Gnani Timbre (`timbre-v2.5` with voice `Saanvi` for Kannada, `Kaveri` for English).

4. **Speech-to-Text Transcription (Prisma STT)**:
   - Child's audio response (WAV/MP3/M4A/FLAC/OGG, <= 60s, <= 10MB) is submitted as multipart data.
   - Streamed in-memory without persistent disk storage; forwarded to `POST https://api.vachana.ai/stt/v3` with `X-API-Key-ID`.
   - Returns a draft transcript saved in `Attempt` with status `pending_confirmation`.

5. **Transcript Correction & Answer Confirmation**:
   - Parent reviews the draft transcript on screen, corrects any misheard words or digits if needed, and explicitly confirms the numeric/option answer.
   - Attempt moves to `confirmed` status.

6. **Deterministic Mathematics Evaluation**:
   - Server-side evaluator evaluates the confirmed answer against the private `evaluator_config`.
   - Supports integers, decimals, multiple choice, and intermediate steps.
   - Returns deterministic pedagogical feedback and appropriate progressive hints.
   - In ambiguous cases, marks attempt as `review_required` rather than guessing.

7. **Teacher Aggregation & Learning Queue**:
   - Protected by `X-Teacher-API-Key`.
   - Delivers anonymized aggregate metrics (sessions started, completed, attempts evaluated, correctness rates) and an anonymized review queue without exposing child identities or session tokens.
