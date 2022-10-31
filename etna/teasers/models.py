from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.images import get_image_model_string


class TeaserImageMixin(models.Model):
    """Mixin to add teaser_image attribute to a Page."""

    teaser_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        abstract = True

    promote_panels = [FieldPanel("teaser_image")]
