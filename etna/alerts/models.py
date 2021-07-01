from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.snippets.models import register_snippet

from ..text_formats.fields import BasicRichTextField


@register_snippet
class Alert(models.Model):
    ALERT_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=100)
    message = BasicRichTextField()
    active = models.BooleanField(default=False)
    cascade = models.BooleanField(default=False, verbose_name='Show on current and all child pages')
    alert_level = models.CharField(max_length=6, choices=ALERT_LEVEL_CHOICES, default='low')

    panels = [
        FieldPanel('title'),
        FieldPanel('message'),
        FieldPanel('active'),
        FieldPanel('cascade'),
        FieldPanel('alert_level'),
    ]

    def __str__(self):
        return self.title
