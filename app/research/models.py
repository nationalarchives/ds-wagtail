from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField

from app.core.models.basepage import BasePageWithIntro
from app.research.blocks import GuidedSearchBlock


class ResearchGuide(BasePageWithIntro):
	guided_search = StreamField(
		[("guided_search", GuidedSearchBlock())],
		blank=True,
		use_json_field=True,
	)
	parent_page_types = ["home.HomePage"]

	content_panels = BasePageWithIntro.content_panels + [FieldPanel("guided_search")]

	api_fields = BasePageWithIntro.api_fields + [APIField("guided_search")]