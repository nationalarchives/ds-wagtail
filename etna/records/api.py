from django.conf import settings

from etna.ciim.client import ClientAPI
from etna.search.delivery_options_api import DeliveryOptionsAPI

""" Search records API """

def get_records_client():
    return ClientAPI(
        base_url=settings.CLIENT_BASE_URL,
        api_key=settings.CLIENT_KEY,
        verify_certificates=settings.CLIENT_VERIFY_CERTIFICATES,
    )


records_client = get_records_client()

""" Delivery Options records API """

def get_delivery_options_client():
    return DeliveryOptionsAPI(
        base_url=settings.DELIVERY_OPTIONS_CLIENT_BASE_URL,
    )


delivery_options_client = get_delivery_options_client()
