from django.db import models
from django.utils.functional import cached_property
from wagtail.admin.panels import FieldPanel
from wagtail.models import Orderable

from .mixins import TagDuplicateCheckMixin

# TODO serializers and API


class KeyStage(models.Model):
    """A model for individual key stage tags - choices are populated by migrations/0002_seed_key_stages.py"""

    name = models.CharField(
        max_length=255,
        verbose_name="name",
        unique=True,
    )

    stage = models.PositiveSmallIntegerField(
        verbose_name="stage",
        help_text="Numeric key stage value, e.g. 2, 3, 4.",
        null=True,
        blank=True,
    )

    age_range = models.CharField(
        max_length=64,
        verbose_name="age range",
        help_text="Age range text, e.g. 5-7 or 7-11.",
        blank=True,
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name="slug",
        unique=True,
    )

    class Meta:
        verbose_name = "Key stage"
        verbose_name_plural = "Key stages"

    @property
    def display_name(self):
        if self.stage and self.age_range:
            return f"Key Stage {self.stage} (ages {self.age_range})"
        return self.name

    @cached_property
    def short_key_stage(self):
        if self.stage is None:
            return self.name
        return f"KS{self.stage}"

    @cached_property
    def public_age_range(self):
        if not self.age_range:
            return ""
        return f"Ages {self.age_range}"

    def __str__(self):
        return self.display_name


class TimePeriod(models.Model):
    """A model for time period tags"""

    name = models.CharField(
        max_length=255,
        verbose_name="name",
        unique=True,
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name="slug",
        unique=True,
    )

    year_from = models.PositiveIntegerField(
        verbose_name="year from",
        null=True,
        blank=True,
        help_text="Starting year, e.g. 1485",
    )

    year_to = models.PositiveIntegerField(
        verbose_name="year to",
        null=True,
        blank=True,
        help_text="Ending year, e.g. 1750",
    )

    available_for_resources = models.BooleanField(
        default=True,
        verbose_name="available for resources",
        help_text="Whether this time period can be tagged on teaching resources.",
    )

    @cached_property
    def display_year_range(self):
        if self.year_from is None and self.year_to is None:
            return ""

        if self.year_from is None:
            return f"pre {self.year_to}"

        if self.year_to is None:
            return f"{self.year_from} - present"

        return f"{self.year_from}-{self.year_to}"

    @cached_property
    def display_name(self):
        year_range = self.display_year_range
        if year_range:
            return f"{self.name} ({year_range})"
        return self.name

    class Meta:
        verbose_name = "Time period"
        verbose_name_plural = "Time periods"

    def __str__(self):
        return self.display_name


class Theme(models.Model):
    """A model for theme tags"""

    name = models.CharField(
        max_length=255,
        verbose_name="name",
        unique=True,
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name="slug",
        unique=True,
    )

    class Meta:
        verbose_name = "Theme"
        verbose_name_plural = "Themes"

    def __str__(self):
        return self.name


class BaseKeyStageTag(TagDuplicateCheckMixin, Orderable):
    FK_FIELD_NAME = "key_stage"
    FIELD_LABEL = "key stage"

    key_stage = models.ForeignKey(
        "education.KeyStage",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name="key stage",
    )

    panels = [
        FieldPanel("key_stage"),
    ]

    class Meta:
        abstract = True


class BaseTimePeriodTag(TagDuplicateCheckMixin, Orderable):
    FK_FIELD_NAME = "time_period"
    FIELD_LABEL = "time period"

    time_period = models.ForeignKey(
        "education.TimePeriod",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name="time period",
    )

    panels = [
        FieldPanel("time_period"),
    ]

    class Meta:
        abstract = True


class BaseThemeTag(TagDuplicateCheckMixin, Orderable):
    FK_FIELD_NAME = "theme"
    FIELD_LABEL = "theme"

    theme = models.ForeignKey(
        "education.Theme",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name="theme",
    )

    panels = [
        FieldPanel("theme"),
    ]

    class Meta:
        abstract = True
