from app.core.blocks.links import InternalLinkBlock
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField, StreamField


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
    links_heading = models.CharField(
        verbose_name=_("links heading"),
        max_length=100,
        blank=True,
        help_text=_("Heading for the links section"),
    )
    links = StreamField(
        [("link", InternalLinkBlock())],
        verbose_name=_("links"),
        blank=True,
        use_json_field=True,
        help_text=_(
            "Add links to internal pages to help users navigate."
        ),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("message"),
        MultiFieldPanel(
            [
                FieldPanel("links_heading"),
                FieldPanel("links"),
            ],
            heading="Links section",
        ),
    ]

    class Meta:
        verbose_name = "Error pages"
