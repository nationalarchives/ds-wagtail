from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.search import index

from wagtailmetadata.utils import get_image_model_string


class SeriesCategory(models.TextChoices):
    RECORD_COLLECTION = "Record collection", "Record collection"


class Series(index.Indexed, models.Model):
    admin_name = models.CharField(
        max_length=128,
        help_text="The name of the series as it should be displayed in the CMS site.",
    )
    category = models.CharField(
        choices=SeriesCategory.choices,
        blank=True,
    )
    image = models.ForeignKey(
        get_image_model_string(), on_delete=models.SET_NULL, null=True, blank=False
    )

    # TODO: Once the real integration with the CIIM search is built,
    #       we should add a field that will allow identify the series
    #       in the CIIM search and on record detail pages.

    panels = [
        FieldPanel("admin_name"),
        FieldPanel("category"),
        FieldPanel("image"),
    ]
    search_fields = [
        index.SearchField("admin_name"),
        index.FilterField("category"),
        index.AutocompleteField("admin_name"),
    ]

    class Meta:
        verbose_name = "series"
        verbose_name_plural = "series"

    def __str__(self) -> str:
        return self.admin_name
