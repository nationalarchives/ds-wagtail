from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

from wagtail.admin.panels import FieldPanel
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
    )

    newly_published_at = models.DateField(
        editable=False,
        default=None,
        null=True,
    )

    NEW_LABEL_DISPLAY_DAYS = 21

    def save(self, *args, **kwargs):
        if self.live and self.mark_new_on_next_publish:
            self.mark_new_on_next_publish = False
            self.newly_published_at = timezone.now().date()
            if self.latest_revision:
                self.latest_revision.content["mark_new_on_next_publish"] = False
                self.latest_revision.content[
                    "newly_published_at"
                ] = self.newly_published_at
                self.latest_revision.save()
        return super().save(*args, **kwargs)

    @cached_property
    def is_newly_published(self):
        expiry_date = timezone.now().date() - timedelta(
            days=self.NEW_LABEL_DISPLAY_DAYS
        )
        if self.newly_published_at:
            if self.newly_published_at > expiry_date:
                return True
        return False

    promote_panels = [
        FieldPanel("mark_new_on_next_publish"),
    ]

    class Meta:
        abstract = True
