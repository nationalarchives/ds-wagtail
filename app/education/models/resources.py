from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable

from app.core.blocks.paragraph import APIRichTextBlock
from app.core.blocks.promoted_links import FeaturedExternalLinkBlock, FeaturedPageBlock
from app.core.blocks.section import SubHeadingBlock
from app.core.models import (
    BasePageWithRequiredIntro,
    ContentWarningMixin,
    PublishedDateMixin,
    RequiredHeroImageMixin,
)
from app.core.serializers import RichTextSerializer

from ..blocks import (
    SourceFeaturedLinkBlock,
    SourceMediaBlock,
    SourceQuestionBlock,
)
from ..serializers import (
    CurriculumConnectionSerializer,
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
        verbose_name=("time period"),
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
        verbose_name=("source title"),
        help_text=("A unique, descriptive title for the source."),
        blank=True,
        max_length=160,
    )

    media = StreamField(
        SourceMediaBlock(),
        verbose_name=("source media"),
        help_text=(
            "Choose one media type for this source. A caption can be added for each."
        ),
        blank=True,
        null=True,
    )

    featured_link = StreamField(
        SourceFeaturedLinkBlock(),
        verbose_name=("source media featured link"),
        help_text=("Choose internal or external link for this source"),
        blank=True,
        max_num=1,
    )

    description = RichTextField(
        features=settings.RESTRICTED_RICH_TEXT_FEATURES,
        verbose_name=("source description"),
        help_text=(
            "An optional free text field to add in a fuller description of the source."
        ),
        blank=True,
        null=True,
    )

    question = StreamField(
        SourceQuestionBlock(
            verbose_name=("source question"),
            help_text=("A series of questions relating to the source."),
        ),
        blank=True,
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("media"),
        FieldPanel("featured_link"),
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
        verbose_name=("Key stage"),
        help_text=("The key stage for this curriculum connection."),
    )

    description = RichTextField(
        features=["bold", "italic", "link", "ul"],
        verbose_name=("curriculum connection description"),
        help_text=("Add the curriculum connection description."),
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
    ContentWarningMixin,
    BasePageWithRequiredIntro,
):
    """A page to display a teaching resource"""

    @cached_property
    def type_label(cls) -> str:
        return "Teaching resource"

    parent_page_types = [
        "education.TeachingResourcesListingPage",
    ]

    enquiry_question = models.CharField(
        verbose_name=("enquiry question"),
        blank=True,
        max_length=160,
    )

    sources_title = models.CharField(
        verbose_name=("sources title"),
        help_text=(
            "Title of the main section of the page. In most cases ‘Investigate the sources’"
        ),
        blank=True,
        max_length=160,
    )

    sources_introduction = RichTextField(
        features=["bold", "italic", "link"],
        verbose_name=("sources introduction"),
        help_text=("Optional text field to provide an introduction to the sources."),
        blank=True,
        null=True,
    )

    teachers_notes = RichTextField(
        features=settings.RESTRICTED_RICH_TEXT_FEATURES,
        verbose_name=("teachers notes"),
        help_text=(
            "A general overview of what the resource contains and how it can be used."
        ),
        blank=True,
        null=True,
    )

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
        verbose_name=("extension activities"),
        help_text=(
            "Optional section where editors can add extra activities for teachers to try with their pupils."
        ),
        blank=True,
        null=True,
    )

    background_information = StreamField(
        [
            (
                "paragraph",
                APIRichTextBlock(features=settings.RESTRICTED_RICH_TEXT_FEATURES),
            ),
            ("sub_heading", SubHeadingBlock()),
        ],
        verbose_name=("background information"),
        help_text=("Section providing historical context to the teaching resource."),
        blank=True,
        null=True,
    )

    further_information_title = models.CharField(
        max_length=255,
        verbose_name=("further information title"),
        help_text=("Title of the further information section."),
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
        verbose_name=("further information"),
        help_text=("Section providing links to other useful information."),
        blank=True,
        null=True,
    )

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + ContentWarningMixin.content_panels
        + [
            FieldPanel("enquiry_question"),
            MultiFieldPanel(
                [
                    FieldPanel("sources_title"),
                    FieldPanel("sources_introduction"),
                    InlinePanel(
                        "sources",
                        label=("Source"),
                        heading=("Sources"),
                        min_num=1,
                    ),
                ],
                heading=("Sources"),
            ),
            FieldPanel("teachers_notes"),
            InlinePanel(
                "curriculum_connections",
                label=("Curriculum connection"),
                heading=("Connections to the curriculum"),
                min_num=1,
            ),
            FieldPanel("extension_activities"),
            FieldPanel("background_information"),
            MultiFieldPanel(
                [
                    FieldPanel("further_information_title"),
                    FieldPanel("further_information"),
                ],
                heading=("Further information"),
            ),
        ]
    )

    promote_panels = (
        PublishedDateMixin.promote_panels
        + BasePageWithRequiredIntro.promote_panels
        + EducationTaxonomyMixin.taxonomy_promote_panels()
    )

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + RequiredHeroImageMixin.api_fields
        + ContentWarningMixin.api_fields
        + [
            PublishedDateMixin.get_published_date_apifield(),
            PublishedDateMixin.get_is_newly_published_apifield(),
        ]
        + [
            APIField("hero_image"),
            APIField("enquiry_question"),
            # TODO: primary tags?
            # APIField("key_stage", serializer=KeyStageSerializer()),
            # APIField("time_period", serializer=TimePeriodSerializer()),
            # APIField("theme", serializer=ThemeSerializer()),
            APIField("key_stages", serializer=KeyStageSerializer(many=True)),
            APIField("time_periods", serializer=TimePeriodSerializer(many=True)),
            APIField("themes", serializer=ThemeSerializer(many=True)),
            APIField("sources_title"),
            APIField("sources_introduction", serializer=RichTextSerializer()),
            APIField("sources", serializer=SourceSerializer(many=True)),
            APIField("teachers_notes"),
            APIField(
                "curriculum_connections",
                serializer=CurriculumConnectionSerializer(many=True),
            ),
            APIField("extension_activities"),
            APIField("background_information"),
            APIField("further_information_title"),
            APIField("further_information"),
        ]
    )
