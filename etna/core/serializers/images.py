from wagtail.images.api.fields import ImageRenditionField

from rest_framework import serializers

def generate_teaser_images(rendition_size: str, jpeg_quality: str, webp_quality: int, source: str = "teaser_image", quality: int = 80):
    """
    This method returns a tuple of two ImageRenditionField instances for the
    given rendition size, JPEG quality and WebP quality. The source parameter
    is used to specify the source image field to use for the rendition.

    To override the default rendition size, quality, or source, you should
    override this in the subclass, following the same structure as teaser_image_jpeg
    and teaser_image_webp below. This will allow for flexibility around the
    types of images that we can supply on a case-by-case basis.

    Args:
    rendition_size: The size of the rendition to return.
    jpeg_quality: The quality of the JPEG rendition.
    webp_quality: The quality of the WebP rendition.
    source: The source image field to use for the rendition - defaults to "teaser_image" if un-set.
    quality: The quality to use for the rendition - only used if no jpeg or webp_quality is set.
    """
    return (
        ImageRenditionField(
            f"{rendition_size}|format-jpeg|jpegquality-{jpeg_quality or quality}",
            source=source,
        ),
        ImageRenditionField(
            f"{rendition_size}|format-webp|webpquality-{webp_quality or quality}",
            source=source,
        ),
    )
