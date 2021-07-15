from django.db import models

from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel


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

    promote_panels = [ImageChooserPanel("teaser_image")]
