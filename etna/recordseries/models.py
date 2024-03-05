from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.images import get_image_model_string
from wagtail.models import LockableMixin, RevisionMixin
from wagtail.search import index


class RecordSeries(LockableMixin, RevisionMixin, index.Indexed, models.Model):
    admin_name = models.CharField(
        max_length=128,
        help_text="The name of the series as it should be displayed in the CMS site.",
    )
    title = models.CharField(max_length=100)
    introduction = models.TextField(max_length=512)
    image = models.ForeignKey(
        get_image_model_string(), on_delete=models.SET_NULL, null=True, blank=False
    )
    show_only_digitised_records = models.BooleanField(default=True)

    # TODO: Once the real integration with the CIIM search is built,
    #       we should add a field that will allow identify the series
    #       in the CIIM search and on record detail pages.

    revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="record_series"
    )

    panels = [
        FieldPanel("admin_name"),
        FieldPanel("title"),
        FieldPanel("introduction"),
        FieldPanel("image"),
        FieldPanel("show_only_digitised_records"),
    ]
    search_fields = [
        index.SearchField("admin_name"),
        index.AutocompleteField("admin_name"),
        index.SearchField("title"),
        index.AutocompleteField("title"),
        index.FilterField("show_only_digitised_records"),
    ]

    class Meta:
        verbose_name = "record series"
        verbose_name_plural = "record series"

    def __str__(self) -> str:
        return self.admin_name
