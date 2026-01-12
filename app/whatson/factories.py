import factory
from app.core.factories import BasePageFactory
from app.whatson import models as app_models
from wagtail_factories import ImageFactory


class WhatsOnPageFactory(BasePageFactory):
    class Meta:
        model = app_models.WhatsOnPage


class EventPageFactory(BasePageFactory):
    lead_image = factory.SubFactory(ImageFactory)
    video_conference_info = ("Video conference info",)
    venue_address = ("Venue address",)
    short_title = ("Short title",)

    class Meta:
        model = app_models.EventPage
