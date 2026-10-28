from app.core.security import generate_session_token, hash_token, verify_teacher_key, verify_token


def test_token_generation_and_hashing():
    token1 = generate_session_token()
    token2 = generate_session_token()
    assert token1 != token2
    assert len(token1) > 20

    hash1 = hash_token(token1)
    assert len(hash1) == 64  # SHA-256 hex string

    assert verify_token(token1, hash1) is True
    assert verify_token(token2, hash1) is False
    assert verify_token("wrong-token", hash1) is False


def test_teacher_key_verification():
    secret = "my-secure-teacher-secret-key"
    assert verify_teacher_key(secret, secret) is True
    assert verify_teacher_key("   my-secure-teacher-secret-key  ", secret) is True
    assert verify_teacher_key("wrong-secret", secret) is False
    assert verify_teacher_key("", secret) is False
    assert verify_teacher_key(None, secret) is False
