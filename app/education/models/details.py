from app.core.blocks.image import APIImageChooserBlock
from app.core.blocks.page_chooser import APIPageChooserBlock
from app.core.blocks.paragraph import APIRichTextBlock
from app.core.blocks.promoted_links import FeaturedExternalLinkBlock, FeaturedPageBlock
from app.core.blocks.section import SubHeadingBlock
from app.core.blocks.video import YouTubeBlock
from app.core.models import (
    BasePageWithRequiredIntro,
    PublishedDateMixin,
    RequiredHeroImageMixin,
)
from app.core.serializers import RichTextSerializer
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable

from ..blocks import (
    QuestionBlock,
    SourceMediaBlock,
)
from ..serializers import (
    KeyStageSerializer,
    SourceSerializer,
    ThemeSerializer,
    TimePeriodSerializer,
)

# TODO: sort panel order on promote tabs


class KeyStage(models.Model):
    """A model for individual key stage tags - choices are populated by migrations/0002_seed_key_stages.py"""

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
        unique=True,
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


class Source(Orderable):
    page = ParentalKey(
        "education.TeachingResourcePage",
        on_delete=models.CASCADE,
        related_name="sources",
    )

    source_title = models.CharField(
        verbose_name=_("source title"),
        help_text=_("A unique, descriptive title for the source."),
        blank=True,
        max_length=160,
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
                SourceMediaBlock(
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

    source_media_caption = StreamField(
        [("source_media_caption", APIRichTextBlock(features=["bold", "italic"]))],
        verbose_name=_("source caption"),
        help_text=_("If provided, displays directly below the source."),
        blank=True,
        null=True,
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
    source_description = StreamField(
        [
            (
                "source_description",
                APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"]),
            )
        ],
        verbose_name=_("source description"),
        help_text=_(
            "An optional free text field to add in a fuller description of the source."
        ),
        blank=True,
        null=True,
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
    )

    curriculum_connection_description = RichTextField(
        features=["bold", "italic", "link", "ul"],
        verbose_name=_("curriculum connection description"),
        help_text=_("Add the curriculum connection description."),
        blank=True,
        null=True,
    )

    panels = [
        FieldPanel("key_stage"),
        FieldPanel("curriculum_connection_description"),
    ]


class TeachingResourcePage(
    BasePageWithRequiredIntro, PublishedDateMixin, RequiredHeroImageMixin
):
    """A page to display a teaching resource"""

    parent_page_types = [
        "education.TeachingResourcesListingPage",
    ]

    enquiry_question = models.CharField(
        verbose_name=_("enquiry question"),
        blank=True,
        max_length=160,
    )

    key_stage = models.ForeignKey(
        "education.KeyStage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("key stage"),
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
    sources_title = models.CharField(
        verbose_name=_("sources title"),
        help_text=_(
            "Title of the main section of the page. In most cases ‘Investigate the sources’"
        ),
        blank=True,
        max_length=160,
    )

    sources_introduction = RichTextField(
        features=["bold", "italic", "link"],
        verbose_name=_("sources introduction"),
        help_text=_("Optional text field to provide an introduction to the sources."),
        blank=True,
        null=True,
    )

    # Teacher’s Notes*
    teachers_notes = StreamField(
        [
            (
                "teachers_notes",
                APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"]),
            )
        ],
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
            (
                "paragraph",
                APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"]),
            ),
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
            (
                "paragraph",
                APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"]),
            ),
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
        help_text=_("Title of the further information section."),
        blank=True,
        null=True,
    )

    further_information = StreamField(
        [
            (
                "paragraph",
                APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"]),
            ),
            ("sub_heading", SubHeadingBlock()),
            ("featured_external_link", FeaturedExternalLinkBlock()),
            ("featured_page", FeaturedPageBlock()),
        ],
        verbose_name=_("further information"),
        help_text=_("Section providing links to other useful information."),
        blank=True,
        null=True,
    )

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            FieldPanel("enquiry_question"),
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
            InlinePanel(
                "curriculum_connections",
                label=_("Curriculum connection"),
                heading=_("Connections to the curriculum"),
                min_num=1,
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
    )

    promote_panels = (
        BasePageWithRequiredIntro.promote_panels
        + PublishedDateMixin.promote_panels
        + [
            FieldPanel("key_stage"),
            FieldPanel("time_period"),
            FieldPanel("theme"),
        ]
    )

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("hero_image"),
        APIField("enquiry_question"),
        APIField("key_stage", serializer=KeyStageSerializer()),
        APIField("time_period", serializer=TimePeriodSerializer()),
        APIField("theme", serializer=ThemeSerializer()),
        APIField("sources_title"),
        APIField("sources_introduction", serializer=RichTextSerializer()),
        APIField("teachers_notes"),
        APIField("sources", serializer=SourceSerializer(many=True)),
        APIField("curriculum_connection_description", serializer=RichTextSerializer()),
        APIField("extension_activities"),
        APIField("background_information"),
        APIField("further_information_title"),
        APIField("further_information"),
    ]


class EducationSessionPage(BasePageWithRequiredIntro, PublishedDateMixin):
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

    promote_panels = (
        BasePageWithRequiredIntro.promote_panels
        + PublishedDateMixin.promote_panels
        + [
            FieldPanel("key_stage"),
            FieldPanel("time_period"),
            FieldPanel("theme"),
        ]
    )

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("key_stage", serializer=KeyStageSerializer()),
        APIField("time_period", serializer=TimePeriodSerializer()),
        APIField("theme", serializer=ThemeSerializer()),
    ]
