from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import InlinePanel, PageChooserPanel
from wagtail.models import Orderable


class EducationTaxonomyMixin:
    """Reusable education taxonomy for common cached properties and panels."""

    @cached_property
    def key_stages(self):
        return [
            tag.key_stage
            for tag in self.education_keystage_tags.select_related("key_stage")
        ]

    @cached_property
    def time_periods(self):
        return [
            tag.time_period
            for tag in self.education_time_period_tags.select_related("time_period")
        ]

    @cached_property
    def themes(self):
        return [tag.theme for tag in self.education_theme_tags.select_related("theme")]

    @cached_property
    def key_stage(self):
        return self.key_stages[0] if self.key_stages else None

    @cached_property
    def time_period(self):
        return self.time_periods[0] if self.time_periods else None

    @cached_property
    def theme(self):
        return self.themes[0] if self.themes else None

    @staticmethod
    def taxonomy_promote_panels():
        return [
            InlinePanel(
                "education_keystage_tags",
                label=_("Key stage"),
                heading=_("Key stages"),
            ),
            InlinePanel(
                "education_time_period_tags",
                label=_("Time period"),
                heading=_("Time periods"),
            ),
            InlinePanel(
                "education_theme_tags",
                label=_("Theme"),
                heading=_("Themes"),
            ),
        ]


class RelatedPageLinkBase(Orderable):
    """Reusable orderable link model for selecting related pages."""

    selected_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("selected page"),
        help_text=_("Navigation to a related page"),
    )

    panels = [
        PageChooserPanel("selected_page"),
    ]

    class Meta:
        abstract = True
        ordering = ["sort_order"]


class TagDuplicateCheckMixin:
    """Mixin to validate that the same tag isn't added twice to a page."""

    # These will be overridden by subclass
    FK_FIELD_NAME = None
    FIELD_LABEL = None

    def clean(self):
        super().clean()
        if self.FK_FIELD_NAME and getattr(self, f"{self.FK_FIELD_NAME}_id"):
            fk_value = getattr(self, self.FK_FIELD_NAME)
            duplicate = (
                self.__class__.objects.filter(
                    page=self.page, **{self.FK_FIELD_NAME: fk_value}
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if duplicate:
                raise ValidationError(
                    {
                        self.FK_FIELD_NAME: _(
                            "This {label} has already been added."
                        ).format(label=self.FIELD_LABEL)
                    }
                )
