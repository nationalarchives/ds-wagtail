from wagtail.images.api.fields import ImageRenditionField

from rest_framework import serializers
from rest_framework.fields import empty


class LinkedPageSerializer(serializers.ModelSerializer):
    """
    This Serializer should be inherited as a base class for all "linked" or "secondary"
    page serializers. It provides a common set of fields that are useful for
    serializing linked pages - otherwise it only provides a page ID.

    Fields returned must be set in the `Meta.fields` attribute of the subclass.
    """

    def teaser_images(
        rendition_size: str,
        jpeg_quality: str,
        webp_quality: int,
        source: str = "teaser_image",
        quality: int = 80,
    ):
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

    title = serializers.CharField()
    url = serializers.SerializerMethodField()
    full_url = serializers.URLField()
    teaser_image_jpeg, teaser_image_webp = teaser_images(
        rendition_size="fill-600x400", jpeg_quality=60, webp_quality=80
    )

    def get_url(self, obj):
        return obj.get_url()

class PageSerializer(serializers.Serializer):
    """
    This Serializer should be inherited as a base class for all "primary" page
    serializers. It provides a common set of fields that are useful for
    serializing primary pages - otherwise it only provides a page ID.

    Fields returned must be set in the `Meta.fields` attribute of the subclass.
    """

    def __init__(
        self,
        instance=None,
        data=empty,
        rendition_size="fill-600x400",
        jpeg_quality=60,
        webp_quality=80,
        **kwargs,
    ):
        self.jpeg_quality = jpeg_quality
        self.webp_quality = webp_quality
        self.rendition_size = rendition_size
        super().__init__(instance=instance, data=data, **kwargs)

    def to_representation(self, instance):
        if not instance:
            return None

        specific = instance.specific
        attributes = {
            "teaser_image": (None, None),
            "type_label": None,
            "is_newly_published": None,
        }

        for attr, default in attributes.items():
            attributes[attr] = getattr(specific, attr, default)

        if attributes["teaser_image"]:
            try:
                jpeg_image = attributes["teaser_image"].get_rendition(
                    f"{self.rendition_size}|format-jpeg|jpegquality-{self.jpeg_quality}"
                )
                webp_image = attributes["teaser_image"].get_rendition(
                    f"{self.rendition_size}|format-webp|webpquality-{self.webp_quality}"
                )
            except AttributeError:
                jpeg_image = webp_image = None
            attributes["teaser_image"] = (jpeg_image, webp_image)

        return {
            "id": specific.id,
            "title": specific.title,
            "teaser_image_jpeg": (
                {
                    "url": jpeg_image.url,
                    "full_url": jpeg_image.full_url,
                    "width": jpeg_image.width,
                    "height": jpeg_image.height,
                }
                if jpeg_image
                else None
            ),
            "teaser_image_webp": (
                {
                    "url": webp_image.url,
                    "full_url": webp_image.full_url,
                    "width": webp_image.width,
                    "height": webp_image.height,
                }
                if webp_image
                else None
            ),
            "type_label": attributes["type_label"](),
            **(
                {"is_newly_published": attributes["is_newly_published"]}
                if attributes["is_newly_published"] is not None
                else {}
            ),
            "url": specific.url,
            "full_url": specific.full_url,
        }
        