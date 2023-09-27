from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import (
    FieldPanel,
    PageChooserPanel,
)
from wagtail.fields import RichTextField, StreamField

from etna.core.models import BasePageWithIntro


class EventPage(BasePageWithIntro):
    """EventPage

    A page for an event.
    """

    # DataLayerMixin overrides
    gtm_content_group = "What's On"

    class Meta:
        verbose_name = _("Event page")

    parent_page_types = ["home.HomePage",]
    subpage_types = []
