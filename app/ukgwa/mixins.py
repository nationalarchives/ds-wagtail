from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField

from .blocks import ExternalLinkBlock


class FeaturedLinksMixin(models.Model):
    """Add featured links section to a page"""

    featured_links_heading = models.CharField(
        verbose_name=_("featured links heading text"),
        max_length=100,
        help_text="A short heading for the featured links section",
    )
    featured_links = StreamField(
        [("link", ExternalLinkBlock())],
        verbose_name=_("featured links"),
        min_num=3,
        max_num=3,
        use_json_field=True,
        help_text=_("Add three external links"),
    )

    class Meta:
        abstract = True

    @staticmethod
    def get_featured_links_panels():
        """Return the panel configuration for featured links"""
        return [
            MultiFieldPanel(
                [
                    FieldPanel("featured_links_heading"),
                    FieldPanel("featured_links"),
                ],
                heading="Featured links",
            )
        ]
