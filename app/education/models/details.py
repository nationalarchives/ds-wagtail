from app.core.blocks.image import APIImageChooserBlock, ContentImageBlock
from app.core.blocks.page_chooser import APIPageChooserBlock
from app.core.blocks.paragraph import APIRichTextBlock
from app.core.blocks.promoted_links import FeaturedExternalLinkBlock, FeaturedPageBlock
from app.core.blocks.section import SubHeadingBlock
from app.core.blocks.video import MixedMediaBlock, YouTubeBlock
from app.core.models import (
    BasePageWithRequiredIntro,
)
from app.media.blocks import MediaBlock
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable

from ..serializers import (
    CurriculumConnectionSerializer,
    KeyStageSerializer,
    ThemeSerializer,
    TimePeriodSerializer,
)


class KeyStageChoices(models.TextChoices):
    KEY_STAGE_1 = "key-stage-1", _("Key Stage 1 (ages 5–7)")
    KEY_STAGE_2 = "key-stage-2", _("Key Stage 2 (ages 7–11)")
    KEY_STAGE_3 = "key-stage-3", _("Key Stage 3 (ages 11–14)")
    KEY_STAGE_4 = "key-stage-4", _("Key Stage 4 (ages 14–16)")
    KEY_STAGE_5 = "key-stage-5", _("Key Stage 5 (ages 16-18)")


KEY_STAGE_ALLOWED_SLUGS = [choice.value for choice in KeyStageChoices]
KEY_STAGE_NAME_CHOICES = [(choice.label, choice.label) for choice in KeyStageChoices]

# Key stage

# Relevant key stage for the resource. Shows on page and also drives filters and search

# Multi select.

# Taken from set taxonomy

# MVP Education Taxonomy


# Time period

# Primary Time period

# Secondary time periods

# Relevant time periods for the resource. Shows on page and also drives filters and search

# Taken from set taxonomy

# MVP Education Taxonomy


# Can only select one primary time period

# Can select multiple secondary time periods


# Theme

# Primary Theme

# Secondary Theme

# Relevant themes for the resource. Shows on page and also drives filters and search

# Taken from set taxonomy

# MVP Education Taxonomy


# Can only select one primary theme

# Can select multiple secondary theme



class KeyStage(models.Model):
    """A model for individual key stage tags"""

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
        choices=KEY_STAGE_NAME_CHOICES,
        unique=True,
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
        choices=KeyStageChoices.choices,
        unique=True,
    )

    class Meta:
        verbose_name = _("Key stage")
        verbose_name_plural = _("Key stages")

    def __str__(self):
        return self.name


class TimePeriod(models.Model):
    """A model for time period tags"""

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
        unique=True,
    )

    class Meta:
        verbose_name = _("Time period")
        verbose_name_plural = _("Time periods")

    def __str__(self):
        return self.name


class Theme(models.Model):
    """A model for theme tags"""

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
        unique=True,
    )

    class Meta:
        verbose_name = _("Theme")
        verbose_name_plural = _("Themes")

    def __str__(self):
        return self.name


class QuestionBlock(blocks.StreamBlock):
    question = blocks.StructBlock(
        [
            (
                "question_heading",
                blocks.CharBlock(
                    required=False,
                    max_length=255,
                ),
            ),
            (
                "guidance_for_teachers",
                APIRichTextBlock(
                    features=["bold", "italic", "link", "ul"],
                    required=False,
                ),
            ),
        ],
        icon="help",
    )


# TODO Source* do as inline panels so multiple can be added

# A document or piece of media for the students to use. In most cases this will be an image or number of images, it may also be a piece of audio, a video or an external link to a resource hosted on a 3rd party platform.

# Ability to add multiple sources to the page. Mandatory to have at least one.

# Required to have atleast one source

# TODO validation for how many sources


class Source(Orderable):
    page = ParentalKey(
        "education.TeachingResourcePage",
        on_delete=models.CASCADE,
        related_name="sources",
    )

    source_title = models.TextField(
        verbose_name=_("source title"),
        help_text=_("A unique, descriptive title for the source."),
        blank=True,
    )

    # Source Media
    source_image = StreamField(
        [
            (
                "source_image",
                APIImageChooserBlock(
                    rendition_size="max-900x900",
                    verbose_name=_("source image"),
                    help_text=_("An image for the source."),
                    blank=True,
                ),
            )
        ],
    )

    source_media = StreamField(
        [
            (
                "source_media",
                MediaBlock(
                    verbose_name=_("source media"),
                    help_text=_("A piece of media for the source."),
                    blank=True,
                ),
            )
        ],
    )

    source_youtube = StreamField(
        [
            (
                "source_youtube",
                YouTubeBlock(
                    verbose_name=_("source youtube video"),
                    help_text=_("A youtube video for the source."),
                    blank=True,
                ),
            )
        ],
    )

    def clean(self):
        super().clean()

        selected_media_fields = [
            field_name
            for field_name in [
                "source_image",
                "source_media",
                "source_youtube",
            ]
            if len(getattr(self, field_name) or []) > 0
        ]

        if len(selected_media_fields) > 1:
            raise ValidationError(
                {
                    field_name: _("Only one source type is allowed per source item.")
                    for field_name in selected_media_fields
                }
            )

    source_media_caption = RichTextField(
        verbose_name=_("source caption"),
        help_text=_("If provided, displays directly below the source."),
        features=["bold", "italic"],
        blank=True,
    )

    # Source link
    source_media_featured_link = StreamField(
        [
            (
                "source_media_featured_link",
                APIPageChooserBlock(
                    label="Internal page",
                    required=False,
                    page_type="wagtailcore.Page",
                ),
            )
        ],
        verbose_name=_("source media featured link"),
        help_text=_("Reference another page published on the site"),
        blank=True,
        max_num=1,
    )

    source_media_featured_external_link = models.URLField(
        verbose_name=_("source media featured link"),
        help_text=_(
            "Option to add link to a resource on a 3rd party platform (e.g. mapping tool)"
        ),
        blank=True,
    )

    # Source description
    source_description = RichTextField(
        verbose_name=_("source description"),
        help_text=_(
            "An optional free text field to add in a fuller description of the source."
        ),
        features=["bold", "italic", "link", "ol", "ul"],
        blank=True,
    )

    # Source questions
    source_question = StreamField(
        QuestionBlock(
            verbose_name=("source question"),
            help_text=("A series of questions relating to each source."),
        ),
        blank=True,
    )

    panels = [
        FieldPanel("source_title"),
        FieldPanel("source_image"),
        FieldPanel("source_media"),
        FieldPanel("source_youtube"),
        FieldPanel("source_media_caption"),
        FieldPanel("source_media_featured_link"),
        FieldPanel("source_media_featured_external_link"),
        FieldPanel("source_description"),
        FieldPanel("source_question"),
    ]


class CurriculumConnection(Orderable):
    page = ParentalKey(
        "education.TeachingResourcePage",
        on_delete=models.CASCADE,
        related_name="curriculum_connections",
    )

    key_stage = models.ForeignKey(
        "education.KeyStage",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Key stage"),
        help_text=_("The key stage for this curriculum connection."),
        limit_choices_to={"slug__in": KEY_STAGE_ALLOWED_SLUGS},
    )

    curriculum_connection_description = RichTextField(
        verbose_name=_("curriculum connection description"),
        help_text=_("Add the curriculum connection description."),
        features=["bold", "italic", "link", "ul"],
        blank=True,
    )

    panels = [
        FieldPanel("key_stage"),
        FieldPanel("curriculum_connection_description"),
    ]


class TeachingResourcePage(BasePageWithRequiredIntro):
    """A page to display a teaching resource"""

    parent_page_types = [
        "education.TeachingResourcesListingPage",
    ]

    # Hero
    hero_image = StreamField(
        [
            (
                "hero_image",
                ContentImageBlock(
                    rendition_size="max-900x900",
                    verbose_name=_("hero image"),
                    blank=True,
                ),
            )
        ],
        null=True,
        max_num=1,
    )

    enquiry_question = models.TextField(
        verbose_name=_("enquiry question"),
        blank=True,
    )

    key_stage = models.ForeignKey(
        "education.KeyStage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("key stage"),
        limit_choices_to={"slug__in": KEY_STAGE_ALLOWED_SLUGS},
    )

    time_period = models.ForeignKey(
        "education.TimePeriod",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("time period"),
    )

    theme = models.ForeignKey(
        "education.Theme",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("theme"),
    )

    # Body
    sources_title = models.TextField(
        verbose_name=_("sources title"),
        help_text=_(
            "Title of the main section of the page. In most cases ‘Investigate the sources’"
        ),
        blank=True,
    )

    sources_introduction = StreamField(
        [("sources_introduction", APIRichTextBlock(features=["bold", "italic", "link"]))],
        verbose_name=_("sources introduction"),
        help_text=_("Optional text field to provide an introduction to the sources."),
        blank=True,
        null=True,
    )

    # Teacher’s Notes*
    teachers_notes = StreamField(
        [("teachers_notes", APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"]))],
        verbose_name=_("teachers notes"),
        help_text=_(
            "A general overview of what the resource contains and how it can be used."
        ),
        blank=True,
        null=True,
    )


    # Extension activities
    extension_activities = StreamField(
        [
            ("paragraph", APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"])),
            ("sub_heading", SubHeadingBlock()),
            ("featured_page", FeaturedPageBlock()),
            ("featured_external_link", FeaturedExternalLinkBlock()),
        ],
        verbose_name=_("extension activities"),
        help_text=_(
            "Optional section where editors can add extra activities for teachers to try with their pupils."
        ),
        blank=True,
        null=True,
    )

    # Background information
    background_information = StreamField(
        [
            ("paragraph", APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"])),
            ("sub_heading", SubHeadingBlock()),
        ],
        verbose_name=_("background information"),
        help_text=_("Section providing historical context to the teaching resource."),
        blank=True,
        null=True,
    )

    # Further information
    further_information_title = models.CharField(
        max_length=255,
        verbose_name=_("further information title"),
        help_text=_("Title of the further information section (required)."),
        blank=True,
        null=True,
    )

    further_information = StreamField(
        [
            ("paragraph", APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"])),
            ("sub_heading", SubHeadingBlock()),
            ("featured_external_link", FeaturedExternalLinkBlock()),
            ("featured_page", FeaturedPageBlock()),
        ],
        verbose_name=_("further information"),
        help_text=_("Section providing links to other useful information."),
        blank=True,
        null=True,
    )

    content_panels = BasePageWithRequiredIntro.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("sources_title"),
                FieldPanel("sources_introduction"),
                InlinePanel(
                    "sources",
                    label=_("Source"),
                    heading=_("Sources"),
                    min_num=1,
                ),
            ],
            heading=_("Sources"),
        ),
        FieldPanel("teachers_notes"),
        MultiFieldPanel(
            [
                InlinePanel(
                    "curriculum_connections",
                    label=_("Curriculum connection"),
                    heading=_("Connections to the curriculum"),
                    min_num=1,
                ),
            ],
            heading=_("Connections to the curriculum"),
        ),
        FieldPanel("extension_activities"),
        FieldPanel("background_information"),
        MultiFieldPanel(
            [
                FieldPanel("further_information_title"),
                FieldPanel("further_information"),
            ],
            heading=_("Further information"),
        ),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("key_stage", serializer=KeyStageSerializer()),
        APIField("time_period", serializer=TimePeriodSerializer()),
        APIField("theme", serializer=ThemeSerializer()),
        APIField(
            "curriculum_connections",
            serializer=CurriculumConnectionSerializer(many=True),
        ),
        APIField("extension_activities"),
        APIField("background_information"),
        APIField("further_information_title"),
        APIField("further_information"),
    ]

class EducationSessionPage(BasePageWithRequiredIntro):
    """A page to display an education session"""

    parent_page_types = [
        "education.EducationSessionsListingPage",
    ]

    key_stage = models.ForeignKey(
        "education.KeyStage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("key stage"),
        limit_choices_to={"slug__in": KEY_STAGE_ALLOWED_SLUGS},
    )

    time_period = models.ForeignKey(
        "education.TimePeriod",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("time period"),
    )

    theme = models.ForeignKey(
        "education.Theme",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("theme"),
    )

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("key_stage", serializer=KeyStageSerializer()),
        APIField("time_period", serializer=TimePeriodSerializer()),
        APIField("theme", serializer=ThemeSerializer()),
    ]


class EducationReadMoreLink(Orderable):
    """Navigation links for the Read more section"""

    page = ParentalKey(
        "education.EducationPage",
        on_delete=models.CASCADE,
        related_name="education_read_more_links",
    )

    selected_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("selected page"),
        help_text=_("Navigation to other sections within Education"),
    )

    panels = [
        PageChooserPanel("selected_page"),
    ]

    class Meta:
        verbose_name = _("read more link")
        ordering = ["sort_order"]
