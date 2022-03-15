from django.conf import settings
from .client import KongClient


kong_client = KongClient(
    base_url=settings.KONG_CLIENT_BASE_URL,
    api_key=settings.KONG_CLIENT_KEY,
    verify_certificates=settings.KONG_CLIENT_VERIFY_CERTIFICATES,
)
