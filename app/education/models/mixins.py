from django.utils.functional import cached_property
from wagtail.admin.panels import InlinePanel


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

    # TODO: Primary tags??? Technically there could be more than one? e.g. keystages
    # @cached_property
    # def key_stage(self):
    #     return self.key_stages[0] if self.key_stages else None

    # @cached_property
    # def time_period(self):
    #     return self.time_periods[0] if self.time_periods else None

    # @cached_property
    # def theme(self):
    #     return self.themes[0] if self.themes else None

    @staticmethod
    def taxonomy_promote_panels():
        return [
            InlinePanel(
                "education_keystage_tags",
                label=("Key stage tag"),
                heading=("Key stages"),
            ),
            InlinePanel(
                "education_time_period_tags",
                label=("Time period tag"),
                heading=("Time periods"),
            ),
            InlinePanel(
                "education_theme_tags",
                label=("Theme tag"),
                heading=("Themes"),
            ),
        ]


class TagDuplicateCheckMixin:
    """Mixin to silently remove duplicate tags for the same FK on the same page.
    Wagtail saves inline panel children before the parent, so validation-on-clean
    is unreliable. Instead, duplicates are automatically removed after save.
    """

    # These will be overridden by subclass
    FK_FIELD_NAME = None
    FIELD_LABEL = None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # After save, remove any other instances with the same page_id and FK value
        if not self.FK_FIELD_NAME:
            return

        page_id = getattr(self, "page_id", None)
        fk_id = getattr(self, f"{self.FK_FIELD_NAME}_id", None)

        if not page_id or not fk_id:
            return

        # Delete any other instances (excluding this one) with the same page and FK
        duplicates = self.__class__.objects.filter(
            page_id=page_id,
            **{f"{self.FK_FIELD_NAME}_id": fk_id},
        ).exclude(pk=self.pk)

        if duplicates.exists():
            duplicates.delete()
