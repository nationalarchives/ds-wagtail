from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.images.api.fields import ImageRenditionField

from etna.core.serializers import RichTextSerializer

from .forms import RequiredHeroImagePageForm

__all__ = [
    "ContentWarningMixin",
    "NewLabelMixin",
    "HeroImageMixin",
    "RequiredHeroImageMixin",
]


class ContentWarningMixin(models.Model):
    """Mixin to allow editors to toggle content warnings on and off"""

    display_content_warning = models.BooleanField(
        verbose_name="display a content warning on this page",
        default=False,
    )

    custom_warning_text = RichTextField(
        verbose_name="custom content warning text (optional)",
        features=["link"],
        blank=True,
        help_text=(
            "If specified, will be used for the content warning. "
            "Otherwise the default text will be used."
        ),
    )

    api_fields = [
        APIField("display_content_warning"),
        APIField("custom_warning_text", serializer=RichTextSerializer()),
    ]

    class Meta:
        abstract = True


class NewLabelMixin(models.Model):
    """Mixin to allow editors to toggle 'new' label to be applied on-publish"""

    mark_new_on_next_publish = models.BooleanField(
        verbose_name="mark this page as 'new' when published",
        default=True,
        help_text="This will set the 'new' label for 21 days",
    )

    newly_published_at = models.DateField(
        editable=False,
        verbose_name="Page marked as new on",
        default=None,
        null=True,
    )

    new_label_display_for_days = 21

    def with_content_json(self, content):
        """
        Overrides Page.with_content_json() to ensure page's `newly_published_at`
        value is always preserved between revisions.
        """
        obj = super().with_content_json(content)
        obj.newly_published_at = self.newly_published_at
        return obj

    def save(self, *args, **kwargs):
        """
        Overrides Page.save() to set `newly_published_at` under the right
        circumstances, and to ensure `mark_new_on_next_publish` is unset
        once that wish has been fulfilled.
        """
        # Set/reset newly_published_at where requested
        if self.live and self.mark_new_on_next_publish:
            self.newly_published_at = timezone.now().date()
            self.mark_new_on_next_publish = False

        # Save page changes to the database
        super().save(*args, **kwargs)

        if self.live and self.mark_new_on_next_publish and self.latest_revision:
            # If `mark_new_on_next_publish` is still 'True' in the latest revision,
            # The checkbox will remain checked when the page is next edited in Wagtail.
            # Checking the box has had the desired effect now, so we 'uncheck' it
            # in the revision content to avoid unexpected resetting.
            self.latest_revision.content["mark_new_on_next_publish"] = False
            self.latest_revision.save()

    @cached_property
    def is_newly_published(self):
        expiry_date = timezone.now().date() - timedelta(
            days=self.new_label_display_for_days
        )
        if self.newly_published_at:
            if self.newly_published_at > expiry_date:
                return True
        return False

    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel("mark_new_on_next_publish"),
                FieldPanel("newly_published_at", read_only=True),
            ],
            heading="New label",
        )
    ]

    class Meta:
        abstract = True

    api_fields = [
        APIField("is_newly_published"),
    ]


class HeroImageMixin(models.Model):
    """Mixin to add hero_image attribute to a Page."""

    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    hero_image_caption = RichTextField(
        verbose_name="hero image caption (optional)",
        features=["bold", "italic", "link"],
        blank=True,
        help_text=(
            "An optional caption for hero images. This could be used for image sources or for other useful metadata."
        ),
    )

    class Meta:
        abstract = True

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("hero_image"),
                FieldPanel("hero_image_caption"),
            ],
            heading="Hero image",
        )
    ]

    api_fields = [
        # APIField("hero_image"),
        APIField("hero_image_caption", serializer=RichTextSerializer()),
        APIField(
            "hero_image_jpg",
            serializer=ImageRenditionField(
                "fill-1200x480|format-jpeg|jpegquality-60", source="hero_image"
            ),
        ),
        APIField(
            "hero_image_webp",
            serializer=ImageRenditionField(
                "fill-1200x480|format-webp", source="hero_image"
            ),
        ),
        APIField(
            "hero_image_jpg_small",
            serializer=ImageRenditionField(
                "fill-600x400|format-jpeg|jpegquality-60", source="hero_image"
            ),
        ),
        APIField(
            "hero_image_webp_small",
            serializer=ImageRenditionField(
                "fill-600x400|format-webp", source="hero_image"
            ),
        ),
    ]


class RequiredHeroImageMixin(HeroImageMixin):
    """Mixin to add hero_image attribute to a Page, and make it required."""

    class Meta:
        abstract = True

    base_form_class = RequiredHeroImagePageForm

    api_fields = HeroImageMixin.api_fields + []
