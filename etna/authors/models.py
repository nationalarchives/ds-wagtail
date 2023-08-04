from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from etna.core.models import BasePage


class AuthorIndexPage(BasePage):
    """Author index page

    This is the parent page for all authors. It is used to
    generate the author index page.
    """

    subpage_types = ["authors.AuthorPage"]

    parent_page_types = ["home.HomePage"]

    @cached_property
    def author_pages(self):
        """Return a sample of child pages for rendering in teaser."""
        return (
            self.get_children()
            .type(AuthorPage)
            .order_by("title")
            .live()
            .specific()[:3]
        )
        


class AuthorPage(BasePage):
    """Author page

    Model to store author details. Including image and a link to
    an external biography page.
    """

    role = models.CharField(blank=True, null=True, max_length=100)
    summary = RichTextField(
        blank=True, null=True, features=settings.INLINE_RICH_TEXT_FEATURES
    )
    image = models.ForeignKey(
        get_image_model_string(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    bio_link = models.URLField(
        blank=False, null=False, help_text="Link to external bio page"
    )
    bio_link_label = models.CharField(
        blank=False, null=False, help_text="Button text for bio link", max_length=50
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("role"),
        FieldPanel("summary"),
        FieldPanel("image"),
        FieldPanel("bio_link"),
        FieldPanel("bio_link_label"),
    ]

    class Meta:
        verbose_name_plural = "Authors"

    parent_page_types = ["authors.AuthorIndexPage"]