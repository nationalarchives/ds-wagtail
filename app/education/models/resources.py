import wagtail.blocks
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
from django.conf import settings
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
from .details import (
    BaseKeyStageTag,
    BaseThemeTag,
    BaseTimePeriodTag,
)
from .mixins import EducationTaxonomyMixin


class TeachingResourcePageKeyStageTag(BaseKeyStageTag):
    page = ParentalKey(
        "education.TeachingResourcePage",
        on_delete=models.CASCADE,
        related_name="education_keystage_tags",
    )


class TeachingResourcePageTimePeriodTag(BaseTimePeriodTag):
    page = ParentalKey(
        "education.TeachingResourcePage",
        on_delete=models.CASCADE,
        related_name="education_time_period_tags",
    )

    time_period = models.ForeignKey(
        "education.TimePeriod",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("time period"),
        limit_choices_to={"available_for_resources": True},
    )


class TeachingResourcePageThemeTag(BaseThemeTag):
    page = ParentalKey(
        "education.TeachingResourcePage",
        on_delete=models.CASCADE,
        related_name="education_theme_tags",
    )


class Source(Orderable):
    page = ParentalKey(
        "education.TeachingResourcePage",
        on_delete=models.CASCADE,
        related_name="sources",
    )

    title = models.CharField(
        verbose_name=_("source title"),
        help_text=_("A unique, descriptive title for the source."),
        blank=True,
        max_length=160,
    )

    # Source Media — choose one type; caption is always included
    media = StreamField(
        [
            (
                "source_image",
                wagtail.blocks.StructBlock(
                    [
                        (
                            "image",
                            APIImageChooserBlock(
                                rendition_size="max-900x900",
                                help_text=_("An image for the source."),
                            ),
                        ),
                        (
                            "caption",
                            APIRichTextBlock(
                                features=["bold", "italic"],
                                required=False,
                                help_text=_("Caption displayed below the image."),
                            ),
                        ),
                    ],
                    label=_("Image"),
                ),
            ),
            (
                "source_media",
                SourceMediaBlock(
                    help_text=_("A piece of audio or video media for the source."),
                ),
            ),
            (
                "source_youtube",
                wagtail.blocks.StructBlock(
                    [
                        (
                            "youtube",
                            YouTubeBlock(
                                help_text=_("A YouTube video for the source."),
                            ),
                        ),
                        (
                            "caption",
                            APIRichTextBlock(
                                features=["bold", "italic"],
                                required=False,
                                help_text=_("Caption displayed below the video."),
                            ),
                        ),
                    ],
                    label=_("YouTube"),
                ),
            ),
        ],
        verbose_name=_("source media"),
        help_text=_(
            "Choose one media type for this source. A caption can be added for each."
        ),
        blank=True,
        null=True,
    )

    # Source link — choose internal or external
    media_featured_link = StreamField(
        [
            (
                "internal_page",
                APIPageChooserBlock(
                    label=_("Internal page"),
                    page_type="wagtailcore.Page",
                    help_text=_("Link to a page published on the site"),
                ),
            ),
            (
                "external_link",
                wagtail.blocks.StructBlock(
                    [
                        (
                            "url",
                            wagtail.blocks.URLBlock(
                                help_text=_(
                                    "Link to a resource on a 3rd party platform (e.g. mapping tool)"
                                ),
                            ),
                        ),
                    ],
                    label=_("External link"),
                ),
            ),
        ],
        verbose_name=_("source media featured link"),
        help_text=_("Choose internal or external link for this source"),
        blank=True,
        max_num=1,
    )

    # Source description
    description = RichTextField(
        features=settings.RESTRICTED_RICH_TEXT_FEATURES,
        verbose_name=_("source description"),
        help_text=_(
            "An optional free text field to add in a fuller description of the source."
        ),
        blank=True,
        null=True,
    )

    # Source questions
    question = StreamField(
        QuestionBlock(
            verbose_name=("source question"),
            help_text=("A series of questions relating to the source."),
        ),
        blank=True,
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("media"),
        FieldPanel("media_featured_link"),
        FieldPanel("description"),
        FieldPanel("question"),
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

    description = RichTextField(
        features=["bold", "italic", "link", "ul"],
        verbose_name=_("curriculum connection description"),
        help_text=_("Add the curriculum connection description."),
        blank=True,
        null=True,
    )

    panels = [
        FieldPanel("key_stage"),
        FieldPanel("description"),
    ]


class TeachingResourcePage(
    EducationTaxonomyMixin,
    PublishedDateMixin,
    RequiredHeroImageMixin,
    BasePageWithRequiredIntro,
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
    teachers_notes = RichTextField(
        features=settings.RESTRICTED_RICH_TEXT_FEATURES,
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
                APIRichTextBlock(features=settings.RESTRICTED_RICH_TEXT_FEATURES),
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
                APIRichTextBlock(features=settings.RESTRICTED_RICH_TEXT_FEATURES),
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
                APIRichTextBlock(features=settings.RESTRICTED_RICH_TEXT_FEATURES),
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
        + EducationTaxonomyMixin.taxonomy_promote_panels()
    )

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("hero_image"),
        APIField("enquiry_question"),
        APIField("key_stage", serializer=KeyStageSerializer()),
        APIField("time_period", serializer=TimePeriodSerializer()),
        APIField("theme", serializer=ThemeSerializer()),
        APIField("key_stages", serializer=KeyStageSerializer(many=True)),
        APIField("time_periods", serializer=TimePeriodSerializer(many=True)),
        APIField("themes", serializer=ThemeSerializer(many=True)),
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
