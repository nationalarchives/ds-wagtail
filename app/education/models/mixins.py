from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import InlinePanel


class EducationTaxonomyMixin:

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
