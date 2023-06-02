from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

from wagtail import blocks
from wagtail.blocks import StructValue
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.images.blocks import ImageChooserBlock


class ImageBlock(blocks.StructBlock):
    """
    An image block which allows editors to ensure accessibility is reflected on the page.
    """

    image = ImageChooserBlock(required=False)
    decorative = blocks.BooleanBlock(
        label=mark_safe(
            "Is this image decorative? <p class='field-title__subheading'>Tick the box if 'yes'</p>"
        ),
        help_text=mark_safe(
            "Decorative images are used for visual effect and do not add information to the content of a page. "
            '<a href="https://www.w3.org/WAI/tutorials/images/decorative/" target="_blank">"Check the guidance to '
            "see if your image is decorative</a>."
        ),
        required=False,
        default=False,
    )

    alt_text = blocks.CharBlock(
        max_length=100,
        label="Image alternative text",
        help_text=mark_safe(
            "Alternative (alt) text describes images when they fail to load, and is read aloud by assistive "
            "technologies. Use a maximum of 100 characters to describe your image. Decorative images do not "
            'require alt text. <a href="https://html.spec.whatwg.org/multipage/images.html#alt" target="_blank">'
            "Check the guidance for tips on writing alt text</a>."
        ),
        required=False,
    )

    caption = blocks.RichTextBlock(
        features=["bold", "italic", "link"],
        help_text=(
            "An optional caption for non-decorative images, which will be displayed directly below the image. "
            "This could be used for image sources or for other useful metadata."
        ),
        label="Caption (optional)",
        required=False,
    )

    def clean(self, value):
        image = value.get("image")
        decorative = value.get("decorative")
        alt_text = value.get("alt_text")
        caption = value.get("caption")

        errors = {}
        if image:
            if not decorative and not alt_text:
                message = "Non-decorative images must contain alt text."
                errors["alt_text"] = ErrorList([message])

            if decorative and alt_text:
                message = "Decorative images should not contain alt text."
                errors["alt_text"] = ErrorList([message])

            if decorative and caption:
                message = """Decorative images should not
                contain a caption to prevent confusing users of assistive technologies."""
                errors["caption"] = ErrorList([message])

        if errors:
            raise StructBlockValidationError(errors)

        return super().clean(value)

    class Meta:
        label = "Image"
        template = "blocks/image-block-default.html"
        help_text = "An image block which allows editors to ensure accessibility is reflected on the page."
        icon = "image"
        form_template = "form_templates/default-form-with-safe-label.html"


class NoCaptionImageBlock(ImageBlock):
    caption = None


class ImageOrientationValue(StructValue):
    def is_portrait(self):
        image = self.get("image")
        if image:
            return image.width < image.height


class ContentImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    alt_text = blocks.CharBlock(
        max_length=100,
        label="Alternative text",
        help_text=mark_safe(
            "Alternative (alt) text describes images when they fail to load, and is read aloud by assistive "
            "technologies. Use a maximum of 100 characters to describe your image. "
            '<a href="https://html.spec.whatwg.org/multipage/images.html#alt" target="_blank">'
            "Check the guidance for tips on writing alt text</a>."
        ),
    )
    caption = blocks.RichTextBlock(
        features=["bold", "italic", "link"],
        help_text=(
            "If provided, displays directly below the image. Can be used to specify sources, transcripts or "
            "other useful metadata."
        ),
        label="Caption (optional)",
        required=False,
    )

    class Meta:
        label = "Image"
        template = "blocks/content_image.html"
        icon = "image"
        form_template = "form_templates/default-form-with-safe-label.html"
        value_class = ImageOrientationValue
