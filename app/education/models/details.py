from app.core.blocks.image import APIImageChooserBlock, ContentImageBlock
from app.core.blocks.paragraph import APIRichTextBlock, ParagraphBlock
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
from wagtail.fields import StreamField
from wagtail.models import Orderable

from ..serializers import KeyStageSerializer, ThemeSerializer, TimePeriodSerializer


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


class KeyStageTag(Orderable):
    """
    This model is used to tag Education pages.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="page_key_stage_tags",
    )

    key_stage = models.ForeignKey(
        "education.KeyStage",
        on_delete=models.CASCADE,
        related_name="key_stage",
        verbose_name=_("Key stage"),
        help_text=_("The key stage of the page."),
        limit_choices_to={"slug__in": KEY_STAGE_ALLOWED_SLUGS},
        null=False,
        blank=False,
    )

    panels = [
        FieldPanel("key_stage"),
    ]

    class Meta:
        verbose_name = _("Key stage")
        verbose_name_plural = _("Key stages")

    def __str__(self):
        return f"{self.page.title}: {self.key_stage.name}"


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
        verbose_name = _("Key stage")
        verbose_name_plural = _("Key stages")

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
        verbose_name = _("Key stage")
        verbose_name_plural = _("Key stages")

    def __str__(self):
        return self.name


class QuestionBlock(blocks.StreamBlock):
    # question_heading = models.TextField(
    #     verbose_name=_("question heading"),
    #     help_text=_(
    #         "A question relating to the resource"
    #     ),
    #     blank=True,
    # )
    question_answer = StreamField(
        [
            (
                "question_answer",
                ParagraphBlock(
                    verbose_name=_("question heading"),
                    help_text=_("A question relating to the resource"),
                    blank=True,
                ),
            )
        ]
    )


# TODO Source* do as inline panels so multiple can be added

# A document or piece of media for the students to use. In most cases this will be an image or number of images, it may also be a piece of audio, a video or an external link to a resource hosted on a 3rd party platform.

# Ability to add multiple sources to the page. Mandatory to have at least one.

# Required to have atleast one source

# TODO validation for how many sources

# "AccordionsBlock",
# "APIPageChooserBlock",
# "ButtonBlock",
# "CodeBlock",
# "CallToActionBlock",
# "ContactBlock",
# "ContentImageBlock",
# "ContentTableBlock",
# "DescriptionListBlock",
# "DetailsBlock",
# "DocumentsBlock",
# "DoDontListBlock",
# "FeaturedExternalLinkBlock",
# "FeaturedCollectionBlock",
# "FeaturedPageBlock",
# "FeaturedPagesBlock",
# "ImageGalleryBlock",
# "InsetTextBlock",
# "PageListBlock",
# "ParagraphBlock",
# "PartnerLogoListBlock",
# "PeopleListingBlock",
# "LargeCardLinksBlock",
# "MixedMediaBlock",
# "QuoteBlock",
# "ReviewBlock",
# "ShopCollectionBlock",
# "SimplifiedAccordionBlock",
# "SubHeadingBlock",
# "SubSubHeadingBlock",
# "WarningTextBlock",
# "YouTubeBlock",


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

    # Source Media TODO
    source_image = StreamField(
        [
            (
                "source_image",
                APIImageChooserBlock(
                    rendition_size="max-900x900",
                    verbose_name=_("sources image"),
                    help_text=_("An image for the source."),
                    blank=True,
                ),
            )
        ],
        max_num=1,
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
        max_num=1,
    )

    source_video = StreamField(
        MixedMediaBlock(
            block_counts={"youtube": {"max_num": 1}, "media": {"max_num": 1}}
        ),
        verbose_name=_("source video"),
        blank=True,
        max_num=1,
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
        max_num=1,
    )

    def clean(self):
        super().clean()

        selected_media_fields = [
            field_name
            for field_name in [
                "source_image",
                "source_media",
                "source_youtube",
                "source_video",
            ]
            if len(getattr(self, field_name) or []) > 0
        ]

        if len(selected_media_fields) > 1:
            raise ValidationError(
                {
                    field_name: _(
                        "Only one source type is allowed per source item."
                    )
                    for field_name in selected_media_fields
                }
            )

    # Editor picks the media associated with the source.

    # Can pick Image, Media, YouTube video.

    # Multi select allowed

    # Media will inherit and show on the page all relevant metadata e.g. transcript, translation, alt text, copyright

    # Note - How to show if an image has an audio transcript?

    # Media caption

    # Option to add a caption to the source e.g. Catalogue reference.

    # Note, if image has copyright metadata, this will show in the  caption field.

    # Rich text - allow bold, italic

    source_media_caption = StreamField(
        [
            (
                "source_media_caption",
                APIRichTextBlock(
                    features=["bold", "italic"],
                    help_text=("If provided, displays directly below the source."),
                    required=False,
                ),
            )
        ]
    )

    # Source link

    # Option to add link to a resource on a 3rd party platform (e.g. mapping tool)

    # Featured external link

    # Featured link

    source_media_featured_link = models.URLField(
        verbose_name=_("source media featured link"),
        help_text=_(
            "Option to add link to a resource on a 3rd party platform (e.g. mapping tool)"
        ),
        blank=True,
    )

    # Source description

    # An optional free text field to add in a fuller description of the source.

    # Rich text - allow bold, italic, hyperlinks, bullets, numbered lists

    source_description = StreamField(
        [("source_description", APIRichTextBlock())],
        help_text=(
            "An optional free text field to add in a fuller description of the source."
        ),
        # required=False,
    )

    # Source questions

    # A series of questions relating to each source.

    # Note: Guidance from TBX, suggests a taxonomy for the question headings, but for ease of migration, use free text Subheadings.

    # Paragraph text (rich text - Bold, Italics, Bulleted list, hyperlink)

    # Subheadings

    source_question = StreamField(
        QuestionBlock(
            verbose_name=("source question"),
            help_text=("Add a series of questions relating to each source."),
            # required=False,
        )
    )

    panels = [
        FieldPanel("source_title"),
        FieldPanel("source_image"),
        FieldPanel("source_media"),
        FieldPanel("source_youtube"),
        FieldPanel("source_media_caption"),
        FieldPanel("source_media_featured_link"),
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

    connection_description = StreamField(
        [
            (
                "connection_description",
                APIRichTextBlock(features=["bold", "italic", "link", "ul"]),
            )
        ],
        help_text=_("Add the curriculum connection description."),
        blank=True,
    )

    panels = [
        FieldPanel("key_stage"),
        FieldPanel("connection_description"),
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
        max_num=1,
    )

    enquiry_question = models.TextField(
        verbose_name=_("enquiry question"),
        help_text=_(
            "???" #TODO: what is this for, is textfield approp
        ),
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

    # TODO ensure this is the right way to do this
    # H2
    # Plain text

    sources_title = models.TextField(
        verbose_name=_("sources title"),
        help_text=_(
            "Title of the main section of the page. In most cases ‘Investigate the sources’"
        ),
        blank=True,
    )

    sources_introduction = StreamField(
        [("sources_introduction", APIRichTextBlock())],
        verbose_name=_("sources introduction"),
        help_text=_("Optional text field to provide an introduction to the sources."),
        blank=True,
    )



    # Teacher’s Notes*

    # Free text field giving a general overview of what the resource contains and how it can be used.

    # Rich text -  allow bold, italic, hyperlinks, bullets, numbered lists


    teachers_notes = StreamField(
        [("teachers_notes", APIRichTextBlock())],
        verbose_name=_("teachers notes"),
        help_text=_("A general overview of what the resource contains and how it can be used."),
        blank=True,
    )


    # Multi add connections:

    # Key stage (select from Key stage taxonomy)

    # Connection description  - Rich text field (bold, italic, hyperlink, bulleted list)




    # Extension activities

    # Optional section where editors can add in extra activities for teachers to try with their pupils

    # Paragraph text

    # Subheadings

    # Featured page

    # Featured external link

    extension_activities = StreamField(
        [
            ("paragraph", ParagraphBlock()),
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

    # Section providing historical context to the teaching resource

    # Paragraph text

    # Subheadings

    background_information = StreamField(
        [
            ("paragraph", ParagraphBlock()),
            ("sub_heading", SubHeadingBlock()),
        ],
        verbose_name=_("background information"),
        help_text=_("Section providing historical context to the teaching resource."),
        blank=True,
        null=True,
    )




    # Further information

    # Section providing links to other useful information.
    # Title of section free text rather than hard coded to give editor flexibility

    # Title*

    # Paragraph text

    # Subheadings

    # Featured external links

    # Featured page

    further_information_title = models.CharField(
        max_length=255,
        verbose_name=_("further information title"),
        help_text=_(
            "Title of the further information section (required)."
        ),
        blank=True,
        null=True,
    )

    further_information = StreamField(
        [
            ("paragraph", ParagraphBlock()),
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
        MultiFieldPanel(
            [
                FieldPanel("teachers_notes"),
            ],
            heading=_("Teacher's notes"),
        ),
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
        MultiFieldPanel(
            [
                FieldPanel("extension_activities"),
            ],
            heading=_("Extension activities"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("background_information"),
            ],
            heading=_("Background information"),
        ),
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
        APIField("extension_activities"),
        APIField("background_information"),
        APIField("further_information_title"),
        APIField("further_information"),
    ]


# META TAB
# Short title


# Internal data

# Teaser text*

# Teaser image


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

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("key_stage", serializer=KeyStageSerializer()),
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
