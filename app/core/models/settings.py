from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField


@register_setting(icon="cog")
class ErrorPageSettings(BaseSiteSetting):
    """
    Site-wide settings including custom error messages.
    """

    title = models.CharField(
        max_length=100,
        default="Page not found",
        help_text=_("Heading"),
    )
    message = RichTextField(
        blank=True,
        null=True,
        features=["link"],
        help_text=_("Custom message to display when a page is not found (404 error)"),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("message"),
    ]

    class Meta:
        verbose_name = "Error pages"
