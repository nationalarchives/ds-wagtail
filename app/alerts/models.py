import time

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet

from .serializers import AlertSerializer, ThemedAlertSerializer


class BaseAlert(models.Model):
    """
    Base Alert snippet

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
    on a single page. These will be listed in hierarchical order.
    """

    name = models.CharField(
        max_length=100,
        help_text="The name of the banner to display in the CMS, for easier identification.",
    )
    title = models.CharField(
        max_length=50,
        help_text="The short title of your banner which will show in bold at the top of the notification banner. E.g. 'Please note' or 'Important information'",
    )
    message = RichTextField(features=settings.INLINE_RICH_TEXT_FEATURES)
    active = models.BooleanField(
        default=False,
        verbose_name="Publish",
    )
    cascade = models.BooleanField(
        default=False, verbose_name="Show on current and all child pages"
    )
    active_from = models.DateTimeField(
        null=True,
        blank=True,
        help_text="If set, the banner will only be visible after this time.",
    )

    active_to = models.DateTimeField(
        null=True,
        blank=True,
        help_text="If set, the banner will not be visible after this time.",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("title"),
        FieldPanel("message"),
        FieldPanel("active"),
        FieldPanel("cascade"),
        FieldPanel("active_from"),
        FieldPanel("active_to"),
    ]

    uid = models.BigIntegerField(null=False, blank=True, editable=False)

    @property
    def is_active_now(self):
        now = timezone.now()

        # Banner has not been published
        if not self.active:
            return False
        if self.active_from and now < self.active_from:
            return False
        elif self.active_to and now >= self.active_to:
            return False

        return self.active

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        now = timezone.now()

        if self.active_from and self.active_from < now:
            raise ValidationError(
                {
                    "active_from": (
                        "Active from (scheduled) date cannot be in the past. If you need to activate this banner immediately, "
                        "please leave the date blank and publish the banner."
                    )
                }
            )

        if self.active_from and self.active_to and self.active_from >= self.active_to:
            raise ValidationError(
                {
                    "active_to": (
                        "Active to (expiry) date must be later than the Active from (scheduled) date."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.uid = round(time.time() * 1000)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class BaseAlertMixin(models.Model):
    """Base mixin with shared alert retrieval logic."""

    def get_active_alert(self, field_name, property_name):
        """
        Find which alert should display on this page.
        """
        page_alert = getattr(self, field_name, None)

        # Look higher in the page tree for cascading alerts
        if parent := self.get_parent():
            inherited_alert = getattr(parent.specific, property_name, None)
            if inherited_alert and inherited_alert.cascade:
                return inherited_alert

        # No cascading parent alert, so use this page's own alert
        if page_alert and page_alert.is_active_now:
            return page_alert

        # No alert found
        return None

    class Meta:
        abstract = True


@register_snippet
class Alert(BaseAlert):
    """Extends BaseAlert adding alert levels.

    alert_level: The level of importance of the alert. Choices are
    "Low", "Medium" and "High". The default is "Low".
    """

    class AlertLevelChoices(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    alert_level = models.CharField(
        max_length=6, choices=AlertLevelChoices.choices, default=AlertLevelChoices.LOW
    )

    panels = BaseAlert.panels + [
        FieldPanel("alert_level"),
    ]


class AlertMixin(BaseAlertMixin):
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

    @property
    def global_alert(self):
        """
        Retrieve the parent-most alert that is active and has cascade enabled.
        If there is no parent alert, then return the current alert if it is active.
        """
        return self.get_active_alert(field_name="alert", property_name="global_alert")

    settings_panels = [FieldPanel("alert")]
    api_fields = [APIField("global_alert", serializer=AlertSerializer())]

    class Meta:
        abstract = True


@register_snippet
class ThemedAlert(BaseAlert):
    """Extends BaseAlert adding alert levels.

    theme: The theme to be applied to the alert. Choices are
    "Green", "Yellow" and "Red". The default is "Green".
    """

    class AlertThemeChoices(models.TextChoices):
        GREEN = "green", "Green"
        YELLOW = "yellow", "Yellow"
        RED = "red", "Red"

    theme = models.CharField(
        max_length=6,
        choices=AlertThemeChoices.choices,
        default=AlertThemeChoices.YELLOW,
    )

    panels = BaseAlert.panels + [
        FieldPanel("theme"),
    ]

    class Meta:
        verbose_name = "Themed Alert"
        verbose_name_plural = "Themed Alerts"


class ThemedAlertMixin(BaseAlertMixin):
    """Alert mixin.

    Add this mixin to pages that require an alert field.
    """

    themed_alert = models.ForeignKey(
        "alerts.ThemedAlert",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    @property
    def global_alert(self):
        """
        Retrieve the parent-most alert that is active and has cascade enabled.
        If there is no parent alert, then return the current alert if it is active.
        """
        return self.get_active_alert(
            field_name="themed_alert", property_name="global_alert"
        )

    settings_panels = [FieldPanel("themed_alert")]
    api_fields = [APIField("global_alert", serializer=ThemedAlertSerializer())]

    class Meta:
        abstract = True
