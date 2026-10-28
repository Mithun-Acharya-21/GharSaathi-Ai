# GharSaathi Maths — REST API Contract

Base URL: `/api/v1`

All requests and responses use JSON unless specified as `multipart/form-data` or `audio/wav`.

---

## 1. Authentication & Security

1. **Anonymous Learning Sessions**:
   - Creating a session returns a high-entropy secret bearer token in `session_token`.
   - Pass on subsequent session operations via header:
     ```http
     Authorization: Bearer <session_token>
     ```
2. **Teacher Reporting**:
   - Protected via pre-shared secret in header:
     ```http
     X-Teacher-API-Key: <teacher_key>
     ```
3. **Correlation ID**:
   - Every request is tagged with an `X-Request-ID` header. If not provided by the client, the server generates a UUID4 and echoes it back in response headers.

---

## 2. Standard Error Response

In case of error, all endpoints return a consistent JSON response:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed: body -> consent_acknowledged: Field required",
    "request_id": "c1f7a0b3-90d1-4e78-9f32-6e2db34b8c91"
  }
}
```

Common status codes:
- `400 Bad Request`: Business validation failure or invalid state transition
- `401 Unauthorized`: Missing or invalid session token or teacher key
- `403 Forbidden`: Consent not acknowledged or access prohibited
- `404 Not Found`: Unknown resource
- `413 Payload Too Large`: Uploaded audio file exceeds limit (10MB)
- `415 Unsupported Media Type`: Audio format not supported
- `422 Unprocessable Content`: Schema validation error
- `429 Too Many Requests`: Transcription quota exceeded (10 per session)
- `502 Bad Gateway`: Upstream Gnani AI service error
- `503 Service Unavailable`: Database offline or service unconfigured
- `504 Gateway Timeout`: Upstream service timed out

---

## 3. Endpoints

### 3.1 Health & Readiness

#### `GET /healthz`
Liveness check.
```json
{
  "status": "ok",
  "app": "GharSaathi Maths API"
}
```

#### `GET /readyz`
Readiness check. Validates PostgreSQL connectivity.
```json
{
  "status": "ready",
  "checks": {
    "database": "ready",
    "app_env": "development"
  }
}
```

---

### 3.2 Activity Catalogue

#### `GET /api/v1/grades`
List supported mathematics grades.
```json
{
  "grades": [
    {
      "grade": 1,
      "name": "Grade 1",
      "description": "Counting, concrete addition and subtraction"
    },
    {
      "grade": 2,
      "name": "Grade 2",
      "description": "Place value, tens and ones grouping"
    },
    {
      "grade": 3,
      "name": "Grade 3",
      "description": "Multiplication as equal groups and repeated addition"
    },
    {
      "grade": 4,
      "name": "Grade 4",
      "description": "Geometry, shapes, measurement and perimeter"
    },
    {
      "grade": 5,
      "name": "Grade 5",
      "description": "Decimals, currency comparison and operations"
    },
    {
      "grade": 6,
      "name": "Grade 6",
      "description": "Ratios, proportions and rate applications"
    }
  ]
}
```

#### `GET /api/v1/activities?grade=3&language_code=kn-IN`
List published activities filtered by grade and language.
```json
{
  "activities": [
    {
      "id": "a3000000-0000-0000-0000-000000000003",
      "grade": 3,
      "subject": "maths",
      "topic": "Multiplication as Equal Groups",
      "learning_objective": "Model multiplication as repeated addition and equal groups using household items.",
      "language_code": "kn-IN",
      "estimated_minutes": 10,
      "question_type": "integer"
    }
  ],
  "total": 1
}
```

#### `GET /api/v1/activities/{activity_id}`
Get the public definition of an activity. Private evaluator configuration is omitted.
```json
{
  "id": "a3000000-0000-0000-0000-000000000003",
  "grade": 3,
  "subject": "maths",
  "topic": "Multiplication as Equal Groups",
  "learning_objective": "Model multiplication as repeated addition and equal groups using household items.",
  "language_code": "kn-IN",
  "estimated_minutes": 10,
  "materials": [
    "12 beads, seeds or buttons (12 ಮಣಿಗಳು ಅಥವಾ ಬೀಜಗಳು)",
    "3 small cups or paper plates (3 ಸಣ್ಣ ಕಪ್ ಅಥವಾ ತಟ್ಟೆಗಳು)"
  ],
  "parent_instructions": "3 ಸಣ್ಣ ಕಪ್‌ಗಳನ್ನು ಮೇಜಿನ ಮೇಲೆ ಇರಿಸಿ...",
  "child_prompt": "3 ಗುಂಪುಗಳಲ್ಲಿ ತಲಾ 4 ಮಣಿಗಳಿವೆ. ಒಟ್ಟು ಎಷ್ಟು ಮಣಿಗಳಿವೆ?",
  "question_type": "integer",
  "public_question_config": {
    "groups": 3,
    "items_per_group": 4,
    "unit": "beads"
  },
  "hints": [
    "ಮೊದಲ ಕಪ್‌ನಲ್ಲಿ 4, ಎರಡನೇ ಕಪ್‌ನಲ್ಲಿ 4, ಮೂರನೇ ಕಪ್‌ನಲ್ಲಿ 4 ಇವೆ. 4 + 4 + 4 ಎಷ್ಟಾಗುತ್ತದೆ?",
    "4 ರ ಮಗ್ಗಿಯನ್ನು 3 ರವರೆಗೆ ಹೇಳಿ: 4 ಒಂದ್ಲ 4, 4 ಎರಡ್ಲ 8, 4 ಮೂರ್ಲ ಎಷ್ಟು?"
  ],
  "content_version": 1,
  "created_at": "2026-10-26T12:00:00Z"
}
```

---

### 3.3 Learning Sessions

#### `POST /api/v1/sessions`
Create an anonymous session. Requires guardian consent acknowledgement.
**Request**:
```json
{
  "activity_id": "a3000000-0000-0000-0000-000000000003",
  "language_code": "kn-IN",
  "consent_acknowledged": true
}
```
**Response (201 Created)**:
```json
{
  "session_id": "67245d8b-5777-4467-b505-1815f917574a",
  "session_token": "u4J59fGZ9e7kH13vQ...",
  "activity": {
    "id": "a3000000-0000-0000-0000-000000000003",
    "grade": 3,
    "subject": "maths",
    "topic": "Multiplication as Equal Groups",
    "learning_objective": "Model multiplication as repeated addition and equal groups using household items.",
    "language_code": "kn-IN",
    "estimated_minutes": 10,
    "question_type": "integer"
  },
  "status": "active",
  "created_at": "2026-10-26T12:05:00Z",
  "expires_at": "2026-10-27T12:05:00Z"
}
```

#### `GET /api/v1/sessions/{session_id}`
Headers: `Authorization: Bearer <session_token>`
```json
{
  "id": "67245d8b-5777-4467-b505-1815f917574a",
  "activity_id": "a3000000-0000-0000-0000-000000000003",
  "language_code": "kn-IN",
  "status": "active",
  "consent_acknowledged": true,
  "created_at": "2026-10-26T12:05:00Z",
  "completed_at": null,
  "expires_at": "2026-10-27T12:05:00Z",
  "attempts": []
}
```

#### `POST /api/v1/sessions/{session_id}/complete`
Headers: `Authorization: Bearer <session_token>`
```json
{
  "session_id": "67245d8b-5777-4467-b505-1815f917574a",
  "status": "completed",
  "completed_at": "2026-10-26T12:15:00Z",
  "message": "Session successfully completed."
}
```

#### `DELETE /api/v1/sessions/{session_id}`
Headers: `Authorization: Bearer <session_token>`
```json
{
  "message": "Session and associated attempt data successfully deleted.",
  "success": true
}
```

---

### 3.4 Speech Transcription & Attempts

#### `POST /api/v1/sessions/{session_id}/attempts/transcribe`
Headers: `Authorization: Bearer <session_token>`
Content-Type: `multipart/form-data`
Field: `audio_file` (WAV, MP3, OGG, FLAC, AAC, M4A)

**Response (201 Created)**:
```json
{
  "attempt_id": "4b68eef0-4822-4a0b-8d82-8407fc29418a",
  "transcription_status": "completed",
  "evaluation_status": "pending_confirmation",
  "transcript": "12",
  "language_code": "kn-IN",
  "provider": "gnani-prisma-v2.5",
  "request_id": "req-019fd17d"
}
```

#### `POST /api/v1/sessions/{session_id}/attempts/text`
Headers: `Authorization: Bearer <session_token>`
**Request**:
```json
{
  "answer": "12"
}
```
**Response (201 Created)**:
```json
{
  "attempt_id": "4b68eef0-4822-4a0b-8d82-8407fc29418a",
  "input_mode": "text",
  "transcription_status": "not_applicable",
  "evaluation_status": "pending_confirmation",
  "draft_answer": "12",
  "message": "Typed answer recorded. Please confirm your answer for evaluation."
}
```

#### `PATCH /api/v1/attempts/{attempt_id}/confirm`
Headers: `Authorization: Bearer <session_token>`
**Request**:
```json
{
  "confirmed_answer": "12",
  "corrected_transcript": "12",
  "confirmation_status": "confirmed"
}
```
**Response**:
```json
{
  "attempt_id": "4b68eef0-4822-4a0b-8d82-8407fc29418a",
  "evaluation_status": "confirmed",
  "confirmed_answer": "12",
  "confirmed_transcript": "12"
}
```

#### `POST /api/v1/attempts/{attempt_id}/evaluate`
Headers: `Authorization: Bearer <session_token>`
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

---

### 3.5 Spoken Instructions (Gnani Timbre TTS)

#### `POST /api/v1/speech/synthesize`
**Request**:
```json
{
  "activity_id": "a3000000-0000-0000-0000-000000000003",
  "text_type": "instructions",
  "language_code": "kn-IN"
}
```
**Response**:
- Status: `200 OK`
- Header: `Content-Type: audio/wav`
- Body: Binary WAV audio data.

---

### 3.6 Teacher Reporting & Review Queue

#### `GET /api/v1/teacher/reports?grade=3`
Headers: `X-Teacher-API-Key: <teacher_key>`
```json
{
  "grade": 3,
  "activities_available": 1,
  "sessions_started": 15,
  "sessions_completed": 12,
  "attempts_evaluated": 20,
  "correct_evaluated_attempts": 17,
  "incorrect_evaluated_attempts": 3,
  "overall_accuracy_percentage": 85.0,
  "review_required_count": 1,
  "topics": [
    {
      "grade": 3,
      "topic": "Multiplication as Equal Groups",
      "sessions_started": 15,
      "sessions_completed": 12,
      "attempts_evaluated": 20,
      "correct_attempts": 17,
      "accuracy_percentage": 85.0,
      "review_required_count": 1
    }
  ]
}
```

#### `GET /api/v1/teacher/review-queue?grade=3`
Headers: `X-Teacher-API-Key: <teacher_key>`
```json
[
  {
    "attempt_id": "9921bc64-16a2-4a09-9bb0-f421f158f918",
    "grade": 3,
    "topic": "Multiplication as Equal Groups",
    "child_prompt": "3 ಗುಂಪುಗಳಲ್ಲಿ ತಲಾ 4 ಮಣಿಗಳಿವೆ. ಒಟ್ಟು ಎಷ್ಟು ಮಣಿಗಳಿವೆ?",
    "input_mode": "speech",
    "draft_transcript": "maybe fifteen beads",
    "confirmed_transcript": "maybe fifteen beads",
    "confirmed_answer": "maybe fifteen beads",
    "evaluation_status": "review_required",
    "feedback": "We could not detect an answer. Would you like to review or try again?",
    "created_at": "2026-10-26T12:20:00Z"
  }
]
```
