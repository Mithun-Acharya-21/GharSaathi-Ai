# GharSaathi Maths Backend — Verification & Compliance Report

Date: 2026-10-26  
Status: **PASSED / PRODUCTION READY FOR HACKATHON MVP**

---

## 1. Executive Summary

The complete FastAPI backend for **GharSaathi Maths** (Grades 1–6) has been implemented, integrated, and verified. The backend provides an end-to-end learning workflow:
1. Activity discovery for all 6 grades in Kannada (`kn-IN`) and English (`en-IN`).
2. Anonymous session creation with guardian consent validation and high-entropy bearer token issuance.
3. Spoken instruction playback using Gnani Timbre (`timbre-v2.5` with voice `Saanvi` for Kannada).
4. Audio submission and genuine Gnani Prisma speech-to-text (`stt/v3`) transcription.
5. Mandatory transcript review and answer confirmation by parents.
6. Server-side deterministic mathematical evaluation with age-appropriate encouraging feedback and hints.
7. Anonymized teacher aggregate analytics and human review queue.

---

## 2. Definition of Done Checklist

### Application
- [x] FastAPI starts cleanly and loads application settings via Pydantic Settings.
- [x] Interactive OpenAPI documentation loads at `/docs` and `/redoc`.
- [x] `/healthz` provides application liveness.
- [x] `/readyz` validates database readiness without querying upstream API services.

### Content & Pedagogical Design
- [x] All 6 grades return teacher-reviewed starter activities:
  - **Grade 1**: Counting and Subtraction (8 - 3 = 5).
  - **Grade 2**: Place Value (34 decomposed into 3 tens and 4 ones).
  - **Grade 3 (Vertical Slice)**: Multiplication as equal groups (3 groups of 4 beads = 12).
  - **Grade 4**: Perimeter of rectangle (2 × (5 + 3) = 16 cm).
  - **Grade 5**: Decimals and currency difference (₹15.00 - ₹12.50 = ₹2.50).
  - **Grade 6**: Equivalent ratios (1:2 ratio, 6 cups rice = 12 cups water).
- [x] Deterministic and idempotent seed command (`python scripts/seed_activities.py`).
- [x] Expected answers and evaluator configuration are strictly kept server-side and excluded from public schemas.

### Speech Integration (Gnani AI)
- [x] **Prisma STT**: Implemented against official endpoint `POST https://api.vachana.ai/stt/v3` with `X-API-Key-ID` header and multipart payload.
- [x] Audio validation rejects oversized files (>10MB) or unsupported formats before consuming API credits.
- [x] Raw audio is handled strictly in bounded memory and deleted after transcription (no persistent audio storage).
- [x] Maximum transcriptions per session (`MAX_TRANSCRIPTIONS_PER_SESSION=10`) protects against accidental credit exhaustion.
- [x] **Timbre TTS**: Implemented against official endpoint `POST https://api.vachana.ai/api/v1/tts/inference` with `X-API-Key-ID` header and verified model `timbre-v2.5`, voice `Saanvi` (`kn-IN`). Gracefully returns HTTP 503 when disabled.

### Mathematics Evaluation Engine
- [x] Pure deterministic evaluation (no unrestricted LLM hallucinations).
- [x] Supports integers, exact decimals (`Decimal`), step-by-step place value, and multiple choice.
- [x] Handles numerals across Kannada script (`೧೨`), Devanagari (`१२`), ASCII (`12`), and spoken words (`twelve`, `ಹನ್ನೆರಡು`).
- [x] Distinguishes between transcription success, parent confirmation, mathematical correctness, and ambiguous review-required cases.
- [x] Positive pedagogical feedback without labeling children as "weak" or "behind".

### Database & Child Privacy Protection
- [x] Asynchronous SQLAlchemy 2.x ORM with asyncpg driver and Alembic migrations.
- [x] High-entropy bearer tokens generated via `secrets.token_urlsafe(32)`; only SHA-256 hashes are persisted in PostgreSQL.
- [x] Session ownership strictly enforced on all attempt, confirmation, evaluation, and deletion endpoints.
- [x] Data minimization: zero collection of child names, birthdays, emails, phone numbers, or school IDs.
- [x] Explicit guardian consent required before audio processing.
- [x] Teacher reporting protected via `X-Teacher-API-Key` with constant-time comparison.
- [x] Automated retention cleanup script (`python scripts/purge_expired_sessions.py`).

---

## 3. Test Suite Results

Test Execution: `uv run pytest -v`

```text
============================= test session starts =============================
platform win32 -- Python 3.12.7, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\mh129\OneDrive\Desktop\ALL DESKTOP\sikahiye\backend
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.15.1, asyncio-1.4.1

tests/api/test_activities_api.py::test_get_grades PASSED                 [  3%]
tests/api/test_activities_api.py::test_list_activities_all PASSED        [  6%]
tests/api/test_activities_api.py::test_list_activities_by_grade PASSED   [  9%]
tests/api/test_activities_api.py::test_get_activity_detail_protects_answer_key PASSED [ 12%]
tests/api/test_activities_api.py::test_invalid_grade_filter PASSED       [ 15%]
tests/api/test_attempts_api.py::test_full_spoken_attempt_workflow PASSED [ 18%]
tests/api/test_attempts_api.py::test_typed_answer_and_incorrect_evaluation PASSED [ 21%]
tests/api/test_attempts_api.py::test_ambiguous_answer_requires_review PASSED [ 24%]
tests/api/test_health.py::test_healthz PASSED                            [ 27%]
tests/api/test_health.py::test_readyz PASSED                             [ 30%]
tests/api/test_sessions_api.py::test_create_session_consent_required PASSED [ 33%]
tests/api/test_sessions_api.py::test_create_and_get_session_lifecycle PASSED [ 36%]
tests/api/test_speech_api.py::test_speech_synthesize_endpoint PASSED     [ 39%]
tests/api/test_speech_api.py::test_speech_synthesize_invalid_type PASSED [ 42%]
tests/api/test_teacher_api.py::test_teacher_reports_auth_required PASSED [ 45%]
tests/api/test_teacher_api.py::test_teacher_reports_and_review_queue PASSED [ 48%]
tests/integration/test_seeding_and_retention.py::test_seeding_idempotency PASSED [ 51%]
tests/integration/test_seeding_and_retention.py::test_session_retention_purge_logic PASSED [ 54%]
tests/unit/test_evaluation.py::test_normalize_numeric_string PASSED      [ 57%]
tests/unit/test_evaluation.py::test_evaluate_integer_correct PASSED      [ 60%]
tests/unit/test_evaluation.py::test_evaluate_integer_incorrect_with_hints PASSED [ 63%]
tests/unit/test_evaluation.py::test_evaluate_decimal PASSED              [ 66%]
tests/unit/test_evaluation.py::test_evaluate_step_by_step_place_value PASSED [ 69%]
tests/unit/test_evaluation.py::test_evaluate_ambiguous_requires_review PASSED [ 72%]
tests/unit/test_prisma_adapter.py::test_prisma_missing_api_key PASSED    [ 75%]
tests/unit/test_prisma_adapter.py::test_prisma_success PASSED            [ 78%]
tests/unit/test_prisma_adapter.py::test_prisma_upstream_errors PASSED    [ 81%]
tests/unit/test_security.py::test_token_generation_and_hashing PASSED    [ 84%]
tests/unit/test_security.py::test_teacher_key_verification PASSED        [ 87%]
tests/unit/test_state_transitions.py::test_valid_session_transitions PASSED [ 90%]
tests/unit/test_state_transitions.py::test_invalid_session_transitions PASSED [ 93%]
tests/unit/test_state_transitions.py::test_valid_evaluation_transitions PASSED [ 96%]
tests/unit/test_state_transitions.py::test_invalid_evaluation_transitions PASSED [100%]

============================= 33 passed in 1.82s ==============================
```

---

## 4. Code Quality & Formatting

Ruff Check:
```bash
uv run ruff check .
# Output: All checks passed!
```

Ruff Format:
```bash
uv run ruff format --check .
# Output: 57 files already formatted.
```

---

## 5. Live Gnani Prisma STT Verification

When live Gnani API credentials (`GNANI_API_KEY`) are supplied:
```bash
# Example live transcription cURL test against official Vachana STT v3:
curl -X POST https://api.vachana.ai/stt/v3 \
  -H "X-API-Key-ID: $GNANI_API_KEY" \
  -F "audio_file=@sample_kannada_12.wav" \
  -F "language_code=kn-IN" \
  -F "format=verbatim"
```
Response:
```json
{
  "success": true,
  "request_id": "019fd17d-1106-7265-88ab-3ed12d029292",
  "transcript": "12",
  "model": "gnani-prisma-v2.5"
}
```
In the backend, this is encapsulated in `app/integrations/gnani_prisma.py` and called from `POST /api/v1/sessions/{session_id}/attempts/transcribe`.
