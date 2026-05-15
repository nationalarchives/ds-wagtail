from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.models import Orderable

# TODO serializers and API


class KeyStage(models.Model):
    """A model for individual key stage tags - choices are populated by migrations/0002_seed_key_stages.py"""

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
        unique=True,
    )

    stage = models.PositiveSmallIntegerField(
        verbose_name=_("stage"),
        help_text=_("Numeric key stage value, e.g. 2, 3, 4."),
        null=True,
        blank=True,
    )

    age_range = models.CharField(
        max_length=64,
        verbose_name=_("age range"),
        help_text=_("Age range text, e.g. 5-7 or 7-11."),
        blank=True,
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
        unique=True,
    )

    class Meta:
        verbose_name = _("Key stage")
        verbose_name_plural = _("Key stages")

    @property
    def display_name(self):
        if self.stage and self.age_range:
            return f"Key Stage {self.stage} (ages {self.age_range})"
        elif self.stage:
            return f"Key Stage {self.stage}"
        else:
            return self.name

    @cached_property
    def public_key_stage(self):
        if self.stage is None:
            return self.name
        return f"Key stage {self.stage}"

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
        verbose_name=_("name"),
        unique=True,
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
        unique=True,
    )

    year_from = models.PositiveIntegerField(
        verbose_name=_("year from"),
        null=True,
        blank=True,
        help_text=_("Starting year, e.g. 1485"),
    )

    year_to = models.PositiveIntegerField(
        verbose_name=_("year to"),
        null=True,
        blank=True,
        help_text=_("Ending year, e.g. 1750"),
    )

    available_for_resources = models.BooleanField(
        default=True,
        verbose_name=_("available for resources"),
        help_text=_("Whether this time period can be tagged on teaching resources."),
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
        unique=True,
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


class BaseKeyStageTag(Orderable):
    key_stage = models.ForeignKey(
        "education.KeyStage",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("key stage"),
    )

    panels = [
        FieldPanel("key_stage"),
    ]

    def clean(self):
        super().clean()
        if self.key_stage_id:
            duplicate = (
                self.__class__.objects.filter(page=self.page, key_stage=self.key_stage)
                .exclude(pk=self.pk)
                .exists()
            )
            if duplicate:
                raise ValidationError(
                    {"key_stage": _("This key stage has already been added.")}
                )

    class Meta:
        abstract = True


class BaseTimePeriodTag(Orderable):
    time_period = models.ForeignKey(
        "education.TimePeriod",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("time period"),
    )

    panels = [
        FieldPanel("time_period"),
    ]

    def clean(self):
        super().clean()
        if self.time_period_id:
            duplicate = (
                self.__class__.objects.filter(
                    page=self.page, time_period=self.time_period
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if duplicate:
                raise ValidationError(
                    {"time_period": _("This time period has already been added.")}
                )

    class Meta:
        abstract = True


class BaseThemeTag(Orderable):
    theme = models.ForeignKey(
        "education.Theme",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("theme"),
    )

    panels = [
        FieldPanel("theme"),
    ]

    def clean(self):
        super().clean()
        if self.theme_id:
            duplicate = (
                self.__class__.objects.filter(page=self.page, theme=self.theme)
                .exclude(pk=self.pk)
                .exists()
            )
            if duplicate:
                raise ValidationError(
                    {"theme": _("This theme has already been added.")}
                )

    class Meta:
        abstract = True
