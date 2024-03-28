from django.conf import settings

from etna.ciim.client import ClientAPI


def get_records_client():
    return ClientAPI(
        base_url=settings.CLIENT_BASE_URL,
        api_key=settings.CLIENT_KEY,
        # TODO: Establish if this is even needed. We could standardise on a different base URL
        #       (without the /api/v1/ suffix) instead.
        iiif_manifest_base_url=settings.CLIENT_IIIF_MANIFEST_BASE_URL,
        verify_certificates=settings.CLIENT_VERIFY_CERTIFICATES,
    )


records_client = get_records_client()
