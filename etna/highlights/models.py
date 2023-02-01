from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet

from etna.records.fields import RecordField


@register_snippet
class Highlight(models.Model):
    title = models.CharField(max_length=255, blank=False, null=True)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    record = RecordField(verbose_name=_("record"))

    date_text = models.CharField(
        verbose_name=_("date text"),
        max_length=100,
        help_text=_("Date(s) related to the record (max. character length: 100)"),
    )

    description = RichTextField(verbose_name=_("description"))

    panels = [
        FieldPanel("title"),
        FieldPanel("image"),
        FieldPanel("record"),
        FieldPanel("date_text"),
        FieldPanel("description"),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "highlight"
        verbose_name_plural = "highlights"
