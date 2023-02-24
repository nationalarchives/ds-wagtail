from django.db import models

from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

__all__ = ["ContentWarningMixin", "NewLabelMixin"]


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


class NewLabelMixin(models.Model):
    """Mixin to allow editors to toggle 'new' label to be applied on-publish"""

    mark_new_on_next_publish = models.BooleanField(
        verbose_name="display a new label on the card of this page",
        default=True,
        help_text="Mark this as true before publishing, if you want to display the 'new label' for 3 weeks",
    )

    newly_published_at = models.DateField(
        editable=False,
        default=None,
        null=True,
    )

    promote_panels = [
        MultiFieldPanel([
            FieldPanel('mark_new_on_next_publish'),
        ]),
    ]

    class Meta:
        abstract = True