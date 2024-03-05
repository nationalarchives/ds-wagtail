from django.conf import settings
from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet


@register_snippet
class Alert(models.Model):
    """Alert snippet.

    Alerts are preconfigured pieces of content that can be selected
    to display on pages with an alert field defined.

    The title and message fields are self-explanatory.

    active: Only active alerts will be displayed. Alert snippets can
    be pre-prepared ready to be activated when required.

    cascade: Enables an alert to be displayed on the current page and
    all child pages of the current page.
    A global alert can be set by selecting it on the Home page and
    setting cascade to True.
    It is possible, through inheritance, for multiple alerts to display
    on a single page. These will be listed in heirarchical order.

    alert_level: The level of importance of the alert. Choices are
    "Low", "Medium" and "High". The default is "Low".
    """

    ALERT_LEVEL_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    title = models.CharField(max_length=100)
    message = RichTextField(features=settings.INLINE_RICH_TEXT_FEATURES)
    active = models.BooleanField(default=False)
    cascade = models.BooleanField(
        default=False, verbose_name="Show on current and all child pages"
    )
    alert_level = models.CharField(
        max_length=6, choices=ALERT_LEVEL_CHOICES, default="low"
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("message"),
        FieldPanel("active"),
        FieldPanel("cascade"),
        FieldPanel("alert_level"),
    ]

    def __str__(self):
        return self.title


class AlertMixin(models.Model):
    """Alert mixin.

    Add this mixin to pages that require an alert field.
    """

    alert = models.ForeignKey(
        "alerts.Alert",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    settings_panels = [
        FieldPanel("alert"),
    ]

    api_fields = [APIField("alert")]

    class Meta:
        abstract = True
