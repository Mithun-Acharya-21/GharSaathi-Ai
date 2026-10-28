import pytest
from httpx import AsyncClient

ACTIVITY_ID = "a3000000-0000-0000-0000-000000000003"


@pytest.mark.asyncio
async def test_full_spoken_attempt_workflow(client: AsyncClient):
    # 1. Create session
    create_res = await client.post(
        "/api/v1/sessions",
        json={
            "activity_id": ACTIVITY_ID,
            "language_code": "kn-IN",
            "consent_acknowledged": True,
        },
    )
    assert create_res.status_code == 201
    session_data = create_res.json()
    session_id = session_data["session_id"]
    token = session_data["session_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload spoken audio for transcription
    fake_wav_bytes = b"RIFF....WAVEfmt ...."
    files = {"audio_file": ("child_answer.wav", fake_wav_bytes, "audio/wav")}
    transcribe_res = await client.post(
        f"/api/v1/sessions/{session_id}/attempts/transcribe",
        headers=headers,
        files=files,
    )
    assert transcribe_res.status_code == 201
    tr_data = transcribe_res.json()
    attempt_id = tr_data["attempt_id"]
    assert tr_data["transcription_status"] == "completed"
    assert tr_data["evaluation_status"] == "pending_confirmation"
    assert tr_data["transcript"] == "12"

    # 3. Trying to evaluate unconfirmed attempt must be rejected
    eval_unconfirmed_res = await client.post(
        f"/api/v1/attempts/{attempt_id}/evaluate", headers=headers
    )
    assert eval_unconfirmed_res.status_code == 400
    assert "confirmed" in eval_unconfirmed_res.json()["error"]["message"].lower()

    # 4. Parent reviews and confirms transcript / numeric answer
    confirm_res = await client.patch(
        f"/api/v1/attempts/{attempt_id}/confirm",
        headers=headers,
        json={"confirmed_answer": "12", "corrected_transcript": "12"},
    )
    assert confirm_res.status_code == 200
    conf_data = confirm_res.json()
    assert conf_data["evaluation_status"] == "confirmed"
    assert conf_data["confirmed_answer"] == "12"

    # 5. Deterministic evaluation
    eval_res = await client.post(f"/api/v1/attempts/{attempt_id}/evaluate", headers=headers)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert eval_data["evaluation_status"] == "evaluated"
    assert eval_data["is_correct"] is True
    assert "ತುಂಬಾ ಒಳ್ಳೆಯದು" in eval_data["feedback"] or "Super" in eval_data["feedback"]
    assert eval_data["review_required"] is False


@pytest.mark.asyncio
async def test_typed_answer_and_incorrect_evaluation(client: AsyncClient):
    # 1. Create session
    create_res = await client.post(
        "/api/v1/sessions",
        json={
            "activity_id": ACTIVITY_ID,
            "language_code": "kn-IN",
            "consent_acknowledged": True,
        },
    )
    session_data = create_res.json()
    session_id = session_data["session_id"]
    token = session_data["session_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Submit typed answer fallback
    text_res = await client.post(
        f"/api/v1/sessions/{session_id}/attempts/text",
        headers=headers,
        json={"answer": "10"},
    )
    assert text_res.status_code == 201
    att_data = text_res.json()
    attempt_id = att_data["attempt_id"]

    # 3. Confirm answer
    await client.patch(
        f"/api/v1/attempts/{attempt_id}/confirm",
        headers=headers,
        json={"confirmed_answer": "10"},
    )

    # 4. Evaluate incorrect answer
    eval_res = await client.post(f"/api/v1/attempts/{attempt_id}/evaluate", headers=headers)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert eval_data["is_correct"] is False
    assert eval_data["next_hint"] is not None
    assert eval_data["review_required"] is False


@pytest.mark.asyncio
async def test_ambiguous_answer_requires_review(client: AsyncClient):
    create_res = await client.post(
        "/api/v1/sessions",
        json={
            "activity_id": ACTIVITY_ID,
            "language_code": "kn-IN",
            "consent_acknowledged": True,
        },
    )
    session_data = create_res.json()
    session_id = session_data["session_id"]
    token = session_data["session_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Typed unclear answer
    text_res = await client.post(
        f"/api/v1/sessions/{session_id}/attempts/text",
        headers=headers,
        json={"answer": "unclear words"},
    )
    attempt_id = text_res.json()["attempt_id"]

    # Confirm
    await client.patch(
        f"/api/v1/attempts/{attempt_id}/confirm",
        headers=headers,
        json={"confirmed_answer": "unclear words"},
    )

    # Evaluate
    eval_res = await client.post(f"/api/v1/attempts/{attempt_id}/evaluate", headers=headers)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert eval_data["review_required"] is True
    assert eval_data["evaluation_status"] == "review_required"
