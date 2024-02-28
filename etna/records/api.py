from django.conf import settings
from etna.ciim.client import ClientAPI


def get_records_client():
    return ClientAPI(
        base_url=settings.CLIENT_BASE_URL,
        api_key=settings.CLIENT_KEY,
        verify_certificates=settings.CLIENT_VERIFY_CERTIFICATES,
    )


records_client = get_records_client()
