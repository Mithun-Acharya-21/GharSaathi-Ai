import hashlib
import hmac
import secrets


def generate_session_token() -> str:
    """Generate a high-entropy random URL-safe bearer token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash a bearer token using SHA-256 for persistent database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_token(plain_token: str, hashed_token: str) -> bool:
    """Verify that a plain token matches the stored SHA-256 hash using constant-time comparison."""
    candidate_hash = hash_token(plain_token)
    return hmac.compare_digest(candidate_hash, hashed_token)


def verify_teacher_key(provided_key: str | None, expected_key: str) -> bool:
    """Verify the teacher API key using constant-time comparison."""
    if not provided_key or not expected_key:
        return False
    return hmac.compare_digest(provided_key.strip(), expected_key.strip())
