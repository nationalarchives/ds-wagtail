from django.conf import settings

from etna.ciim.client import KongClient

from .models import Record


def get_records_client():
    return KongClient(
        base_url=settings.KONG_CLIENT_BASE_URL,
        api_key=settings.KONG_CLIENT_KEY,
        record_class=Record,
        verify_certificates=settings.KONG_CLIENT_VERIFY_CERTIFICATES,
    )


records_client = get_records_client()
