from django.db import models

from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel


class HeroImageMixin(models.Model):
    """Mixin to add hero_image attribute to a Page."""

    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        abstract = True

    content_panels = [ImageChooserPanel("hero_image")]
