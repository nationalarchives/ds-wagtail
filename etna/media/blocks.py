from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.html import mark_safe, escape

from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock

class MediaChooserBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        """
        AbstractMediaChooserBlock requires this method to be defined
        even though it is only called if no template is specified.

        https://github.com/wagtail/wagtail/blob/8413d00bdd03c447900019961d604186e17d2870/wagtail/core/blocks/base.py#L206
        """
        pass


class MediaBlock(blocks.StructBlock):
    """
    Embedded media block with a selectable background image.
    """
    background_image = ImageChooserBlock(
        help_text="A background image for the media block"
    )
    media = MediaChooserBlock()

    class Meta:
        template = "media/blocks/media-block.html"
        help_text = "An embedded audio or video block"
        icon = "fa-play"



class ImageBlock(blocks.StructBlock):
    """
    An image block which allows editors to ensure accessibility is reflected on the page.
    """
    image = ImageChooserBlock(required=True)
    decorative = blocks.BooleanBlock(
        
    label=mark_safe("%s <p style='font-size: 11px;'>%s</p>" % (
    
    escape("Is this image decorative?"),
    escape("Tick the box if 'yes'")
    
    )), 
    help_text=
    mark_safe("%s <a href=%s target=%s>%s</a>." % (
            escape("Decorative images are used for visual effect and do not add information to the content of a page."),
            escape("https://www.w3.org/WAI/tutorials/images/decorative/"),
            escape("_blank"),
            escape("Check the guidance to see if your image is decorative")
        )), required=False, default=False)
    alt_text = blocks.CharBlock(max_length=100, label="Image alternative text", help_text=
    mark_safe("%s <a href=%s target=%s>%s</a>." % (
            escape("Alternative (alt) text describes images when they fail to load, and is read aloud by assistive technologies. Use a maximum of 100 characters to describe your image. Decorative images do not require alt text."),
            escape("https://html.spec.whatwg.org/multipage/images.html#alt"),
            escape("_blank"),
            escape("Check the guidance for tips on writing alt text")
    )), required=False)
    caption = blocks.RichTextBlock(features=['link'], help_text="An optional caption for non-decorative images, which will be displayed directly below the image. This could be used for image sources or for other useful metadata.", label="Caption (optional)", required=False)

    def clean(self, value):
        decorative = value.get("decorative")
        alt_text = value.get("alt_text")
        caption = value.get("caption")

        errors = {}

        if not decorative and not alt_text:
            message = "Non-decorative images must contain alt-text."
            errors["alt_text"] = ErrorList([message])  

        if decorative and alt_text:
            message = "Decorative images should not contain alt text."
            errors["alt_text"] = ErrorList([message]) 
            
        if decorative and caption:
            message = "Decorative images should not contain a caption to prevent confusing users of assistive technologies."
            errors["caption"] = ErrorList([message]) 

        if errors:
            raise ValidationError("There was a validation error with your image.", params=errors)

        return super().clean(value)

    class Meta:
        template = "media/blocks/image-block-default.html"
        help_text = "An image block which allows editors to ensure accessibility is reflected on the page."
        icon = "fa-image"
