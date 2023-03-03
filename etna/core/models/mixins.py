from datetime import datetime, timedelta

from django.db import models
from django.utils.functional import cached_property

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField

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
        verbose_name="mark this page as 'new' when published",
        default=True,
        help_text="Mark this as true before publishing, to display the 'new label'",
    )

    newly_published_at = models.DateField(
        editable=False,
        default=None,
        null=True,
    )

    new_label_end_date = 21

    def with_content_json(self, content):
        obj = super().with_content_json(content)
        if obj.mark_new_on_next_publish:
            obj.mark_new_on_next_publish = False
            obj.newly_published_at = datetime.now().date()
        return obj

    @cached_property
    def is_newly_published(self):
        expiry_date = datetime.now().date() - timedelta(days=self.new_label_end_date)
        if self.newly_published_at is not None:
            if self.newly_published_at > expiry_date:
                return True
        return False

    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel("mark_new_on_next_publish"),
            ]
        ),
    ]

    class Meta:
        abstract = True
