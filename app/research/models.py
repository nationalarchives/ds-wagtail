from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.fields import StreamField
from modelcluster.fields import ParentalKey

from app.ciim.fields import RecordField
from app.generic_pages.blocks import GeneralPageStreamBlock
from app.core.models.basepage import BasePageWithIntro
from app.research.blocks import GuidedSearchBlock

class RelatedRecord(models.Model):
	page = ParentalKey(
		"research.ResearchGuide",
		on_delete=models.CASCADE,
		related_name="related_records",
	)
	record = RecordField(
        verbose_name="record",
        db_index=True,
        blank=False,
        null=False,
        help_text="Enter the IAID for the record which this guide relates to",
    )
	description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

	class Meta:
		verbose_name = "Related Record"
		verbose_name_plural = "Related Records"

	def __str__(self):
		return str(self.record)

class ResearchGuide(BasePageWithIntro):
	guided_search = StreamField(
		[("guided_search", GuidedSearchBlock())],
		blank=True,
		use_json_field=True,
	)
	body = StreamField(GeneralPageStreamBlock, blank=True, null=True)

	parent_page_types = ["home.HomePage"]

	content_panels = BasePageWithIntro.content_panels + [FieldPanel("guided_search"), FieldPanel("body")]

	promote_panels = BasePageWithIntro.promote_panels + [
		InlinePanel("related_records", label="Related Records")
	]

	api_fields = BasePageWithIntro.api_fields + [APIField("guided_search"), APIField("body")]