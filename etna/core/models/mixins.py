from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string

from etna.core.serializers import (
    DetailedImageSerializer,
    ImageSerializer,
    RichTextSerializer,
)

from .forms import RequiredHeroImagePageForm

__all__ = [
    "AccentColourMixin",
    "ContentWarningMixin",
    "NewLabelMixin",
    "HeroImageMixin",
    "RequiredHeroImageMixin",
    "SidebarMixin",
    "SocialMixin",
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

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("display_content_warning"),
                FieldPanel("custom_warning_text"),
            ],
            heading="Content Warning Options",
            classname="collapsible",
        ),
    ]

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
        APIField("hero_image_caption", serializer=RichTextSerializer()),
        APIField(
            "hero_image",
            serializer=DetailedImageSerializer("fill-1200x480"),
        ),
        APIField(
            "hero_image_small",
            serializer=DetailedImageSerializer("fill-600x400", source="hero_image"),
        ),
    ]


class RequiredHeroImageMixin(HeroImageMixin):
    """Mixin to add hero_image attribute to a Page, and make it required."""

    class Meta:
        abstract = True

    base_form_class = RequiredHeroImagePageForm


class AccentColourChoices(models.TextChoices):
    """
    This model is a list of our accent colours, which can be used
    for various components on the site.
    """

    NONE = "none", _("None")
    BLACK = "Black", _("Black")
    PINK = "Pink", _("Pink")
    ORANGE = "Orange", _("Orange")
    YELLOW = "Yellow", _("Yellow")
    GREEN = "Green", _("Green")
    BLUE = "Blue", _("Blue")


class AccentColourMixin(models.Model):
    """Mixin to add accent_colour attribute to a Page."""

    accent_colour = models.CharField(
        max_length=20,
        default=AccentColourChoices.NONE,
        verbose_name=_("hero text colour"),
        help_text=_("The accent colour of the page where relevant."),
        choices=AccentColourChoices.choices,
    )

    class Meta:
        abstract = True

    content_panels = [
        FieldPanel("accent_colour"),
    ]

    api_fields = [
        APIField("accent_colour"),
    ]


class SidebarMixin(models.Model):
    """Mixin to add sidebar options to a Page."""

    page_sidebar = models.CharField(
        choices=[
            ("contents", "Contents"),
            ("sections", "Sections"),
            ("section_tabs", "Section tabs"),
            ("pages", "Pages"),
            ("pages_tabs", "Pages tabs"),
        ],
        help_text=mark_safe(
            "Select the sidebar style for this page. For more information, see the <a href='https://nationalarchives.github.io/design-system/components/sidebar/'>sidebar documentation</a>."
        ),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    settings_panels = [
        FieldPanel("page_sidebar"),
    ]

    api_fields = [
        APIField("page_sidebar"),
    ]


class SocialMixin(models.Model):
    """Mixin to add social media sharing options to a Page."""

    search_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("OpenGraph image"),
        help_text=_(
            "Image that will appear when this page is shared on social media. This will default to the teaser image if left blank."
        ),
    )

    twitter_og_title = models.CharField(
        verbose_name=_("Twitter OpenGraph title"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("If left blank, the OpenGraph title will be used."),
    )
    twitter_og_description = models.TextField(
        verbose_name=_("Twitter OpenGraph description"),
        blank=True,
        null=True,
        help_text=_("If left blank, the OpenGraph description will be used."),
    )
    twitter_og_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Twitter OpenGraph image"),
        help_text=_("If left blank, the OpenGraph image will be used."),
    )

    class Meta:
        abstract = True

    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel("teaser_text"),
                FieldPanel("teaser_image"),
            ],
            heading="Internal data",
        ),
        MultiFieldPanel(
            [
                FieldPanel(
                    "seo_title",
                    help_text=_(
                        "The name of the page displayed on search engine results as the clickable headline and when shared on social media."
                    ),
                ),
                FieldPanel(
                    "search_description",
                    help_text=_(
                        "The descriptive text displayed underneath a headline in search engine results and when shared on social media."
                    ),
                ),
                FieldPanel("search_image"),
            ],
            heading="Base OpenGraph data",
        ),
        MultiFieldPanel(
            [
                FieldPanel("twitter_og_title"),
                FieldPanel("twitter_og_description"),
                FieldPanel("twitter_og_image"),
            ],
            heading="Twitter OpenGraph data",
        ),
    ]

    api_meta_fields = [
        APIField(
            "teaser_image_square",
            serializer=ImageSerializer("fill-512x512", source="teaser_image"),
        ),
        APIField("seo_title"),
        APIField("search_description"),
        APIField(
            "search_image",
            serializer=ImageSerializer("fill-1200x630"),
        ),
        APIField("twitter_og_title"),
        APIField("twitter_og_description"),
        APIField(
            "twitter_og_image",
            serializer=ImageSerializer("fill-1200x630"),
        ),
    ]
