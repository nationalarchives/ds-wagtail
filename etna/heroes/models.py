from django.db import models
from django.db.models.fields import Field

from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.core.fields import RichTextField
from django.utils.html import format_html
from wagtail.admin.edit_handlers import MultiFieldPanel, FieldPanel

from .forms import PageWithHeroMixinForm

class HeroImageMixin(models.Model):
    """Mixin to add hero_image attribute to a Page."""

    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    hero_image_decorative = models.BooleanField(
        verbose_name="this image is purely decorative",
        help_text=format_html(
            "%s <a href=%s target=%s>%s</a>."
            % (
                "Decorative images are used for visual effect and do not add information to the content of a page.",
                "https://www.w3.org/WAI/tutorials/images/decorative/",
                "_blank",
                "Check the guidance to see if your image is decorative",
            )
        ),
        default=False,
    )

    hero_image_alt_text = models.CharField(
        max_length=100,
        blank=True,
        help_text=format_html(
            "%s <a href=%s target=%s>%s</a>."
            % (
                """Alternative (alt) text describes images when they fail to load,
        and is read aloud by assistive technologies.
        Use a maximum of 100 characters to describe your image.
        Decorative images do not require alt text.""",
                "https://html.spec.whatwg.org/multipage/images.html#alt",
                "_blank",
                "Check the guidance for tips on writing alt text",
            )
        ),
    )

    hero_image_caption = RichTextField(
        verbose_name="hero image caption (optional)",
        features=["link"],
        blank=True,
        help_text="""An optional caption for non-decorative images, which will be displayed
         directly below the image.
         This could be used for image sources or for other useful metadata.""",
    )

    class Meta:
        abstract = True

    content_panels = [MultiFieldPanel([ImageChooserPanel("hero_image"), FieldPanel("hero_image_decorative"), FieldPanel("hero_image_alt_text"), FieldPanel("hero_image_caption")], heading="Hero image (optional)")]

    base_form_class = PageWithHeroMixinForm
