import hmac

from uuid import UUID

from django.conf import settings


def sign_submission_id(id: UUID) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(), str(id).encode(), "sha256"
    ).hexdigest()


def get_allowed_hosts() -> list[str]:
    allowed_hosts = settings.ALLOWED_HOSTS
    if settings.DEBUG and not allowed_hosts:
        # Allow variants of localhost in local development
        return [".localhost", "127.0.0.1", "0.0.0.0", "[::1]"]
    return allowed_hosts


def normalize_path(value: str) -> str:
    """
    Ensure 'path' value:
    1. Is lower-case
    2. Has no presceding or trailing whitespace
    3. Starts with a '/'
    """
    return "/" + value.lower().lstrip("/").strip()
