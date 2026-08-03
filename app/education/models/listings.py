from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.timezone import localdate
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField

from app.core.models import (
    BasePageWithRequiredIntro,
    RequiredHeroImageMixin,
)
from app.core.serializers import DefaultPageSerializer
from app.education.models.sessions import (
    EducationSessionPage,
    EducationSessionPageKeyStageTag,
    EducationSessionPageThemeTag,
    EducationSessionPageTimePeriodTag,
    SessionLocation,
)

from ..serializers import KeyStageSerializer, ThemeSerializer, TimePeriodSerializer
from .details import KeyStage, Theme, TimePeriod
from .resources import (
    TeachingResourcePage,
    TeachingResourcePageKeyStageTag,
    TeachingResourcePageThemeTag,
    TeachingResourcePageTimePeriodTag,
)


class TeachingResourcesListingPage(RequiredHeroImageMixin, BasePageWithRequiredIntro):
    """
    A page for displaying education/teaching resources.
    """

    @cached_property
    def type_label(self) -> str:
        return "Education"

    parent_page_types = [
        "education.EducationPage",
    ]

    subpage_types = [
        "education.TeachingResourcePage",
    ]

    max_count = 1

    @cached_property
    def search_filters(self):
        resource_pages = TeachingResourcePage.objects.live().public()

        key_stages = (
            TeachingResourcePageKeyStageTag.objects.filter(page__in=resource_pages)
            .values_list("key_stage", flat=True)
            .distinct()
        )
        time_periods = (
            TeachingResourcePageTimePeriodTag.objects.filter(page__in=resource_pages)
            .values_list("time_period", flat=True)
            .distinct()
        )
        themes = (
            TeachingResourcePageThemeTag.objects.filter(page__in=resource_pages)
            .values_list("theme", flat=True)
            .distinct()
        )

        return {
            "key_stage": KeyStageSerializer(
                KeyStage.objects.filter(id__in=key_stages).order_by("stage", "name"),
                many=True,
            ).data,
            "time_period": TimePeriodSerializer(
                TimePeriod.objects.filter(id__in=time_periods).order_by(
                    "year_from", "year_to", "name"
                ),
                many=True,
            ).data,
            "theme": ThemeSerializer(
                Theme.objects.filter(id__in=themes).order_by("name"),
                many=True,
            ).data,
        }

    featured_teaching_resource = models.ForeignKey(
        "education.TeachingResourcePage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="featured teaching resource",
        help_text="Option to add a highlighted teaching resource, particularly for history months etc",
    )

    featured_teaching_resource_teaser_override = models.CharField(
        verbose_name="Featured teaching resource teaser text override",
        help_text="Override text for the featured teaching resource",
        blank=True,
        max_length=160,
    )

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            MultiFieldPanel(
                [
                    PageChooserPanel("featured_teaching_resource"),
                    FieldPanel("featured_teaching_resource_teaser_override"),
                ],
                heading="Featured teaching resource",
            ),
        ]
    )

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("featured_teaching_resource", serializer=DefaultPageSerializer()),
        APIField("featured_teaching_resource_teaser_override"),
        APIField("search_filters"),
    ]

    class Meta:
        verbose_name = "Teaching Resources listing page"


class EducationSessionsListingPage(BasePageWithRequiredIntro):
    """
    A page for displaying education sessions.
    """

    @cached_property
    def type_label(self) -> str:
        return "Education"

    parent_page_types = [
        "education.EducationPage",
    ]

    subpage_types = [
        "education.EducationSessionPage",
    ]

    max_count = 1

    @cached_property
    def search_filters(self):
        today = localdate()
        current_or_future_session_pages = (
            EducationSessionPage.objects.live()
            .public()
            .filter(
                Q(start_date__gte=today)
                | Q(end_date__gte=today)
                | Q(start_date__isnull=True, end_date__isnull=True)  # all year round
            )
        )

        key_stages = (
            EducationSessionPageKeyStageTag.objects.filter(
                page__in=current_or_future_session_pages
            )
            .values_list("key_stage", flat=True)
            .distinct()
        )
        time_periods = (
            EducationSessionPageTimePeriodTag.objects.filter(
                page__in=current_or_future_session_pages
            )
            .values_list("time_period", flat=True)
            .distinct()
        )
        themes = (
            EducationSessionPageThemeTag.objects.filter(
                page__in=current_or_future_session_pages
            )
            .values_list("theme", flat=True)
            .distinct()
        )

        available_location_types = set(
            SessionLocation.objects.filter(page__in=current_or_future_session_pages)
            .exclude(location_type__isnull=True)
            .exclude(location_type=SessionLocation.LocationType.CUSTOM)
            .values_list("location_type", flat=True)
            .distinct()
        )

        available_regions = set(
            SessionLocation.objects.filter(page__in=current_or_future_session_pages)
            .exclude(region__isnull=True)
            .exclude(region="")
            .values_list("region", flat=True)
            .distinct()
        )

        return {
            "key_stage": KeyStageSerializer(
                KeyStage.objects.filter(id__in=key_stages).order_by("stage", "name"),
                many=True,
            ).data,
            "time_period": TimePeriodSerializer(
                TimePeriod.objects.filter(id__in=time_periods).order_by(
                    "year_from", "year_to", "name"
                ),
                many=True,
            ).data,
            "theme": ThemeSerializer(
                Theme.objects.filter(id__in=themes).order_by("name"),
                many=True,
            ).data,
            "location": [
                {
                    "name": label,
                    "slug": value,
                }
                for value, label in SessionLocation.LocationType.choices
                if value in available_location_types
            ],
            "region": [
                {
                    "name": label,
                    "slug": value,
                }
                for value, label in SessionLocation.Regions.choices
                if value in available_regions
            ],
        }

    featured_education_session = models.ForeignKey(
        "education.EducationSessionPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="featured education session",
        help_text="Page picker to highlight a featured education session",
    )

    featured_education_session_teaser_override = models.CharField(
        verbose_name="Featured education session teaser text override",
        help_text="Override text for the featured education session",
        blank=True,
        max_length=160,
    )

    content_panels = BasePageWithRequiredIntro.content_panels + [
        MultiFieldPanel(
            [
                PageChooserPanel("featured_education_session"),
                FieldPanel("featured_education_session_teaser_override"),
            ],
            heading="Featured education session",
        ),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField(
            "featured_education_session",
            serializer=DefaultPageSerializer(
                required_api_fields=["session_locations", "start_date", "end_date"]
            ),
        ),
        APIField("featured_education_session_teaser_override"),
        APIField("search_filters"),
    ]

    class Meta:
        verbose_name = "Education Sessions listing page"
