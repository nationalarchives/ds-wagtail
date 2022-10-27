from django.db import models
from wagtail.admin.panels import FieldPanel
from ..records.blocks import RecordChooserBlock

class Highlights(models.Model):
    title = models.CharField(max_length=255)
    standfirst = models.CharField(max_length=255)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    record = RecordChooserBlock()
    date = models.CharField(max_length=20)

    panels = [
        FieldPanel('title'),
        FieldPanel('standfirst'),
        FieldPanel('image'),
        FieldPanel('record'),
        FieldPanel('date')
    ]