from django.conf import settings

from etna.ciim.client import KongClient


def get_records_client():
    return KongClient(
        base_url=settings.CLIENT_BASE_URL,
        api_key=settings.CLIENT_KEY,
        verify_certificates=settings.CLIENT_VERIFY_CERTIFICATES,
    )


records_client = get_records_client()
