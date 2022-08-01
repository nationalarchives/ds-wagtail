from django.db import models

from wagtail.fields import RichTextField

__all__ = ["ContentWarningMixin"]


class ContentWarningMixin(models.Model):
    """Mixin to allow editors to toggle content warnings on and off"""

    display_content_warning = models.BooleanField(
        verbose_name="display a content warning on this page",
        default=False,
    )

    custom_warning_text = RichTextField(
        verbose_name="custom content warning text (optional)",
        features=["link"],
        blank=True,
        help_text=(
            "If specified, will be used for the content warning. "
            "Otherwise the default text will be used."
        ),
    )

    class Meta:
        abstract = True
