from app.api.permissions import IsAPITokenAuthenticated
from app.core.serializers.images import image_generator
from django.conf import settings
from django.urls import path
from rest_framework.response import Response
from wagtail.images.api.v2.serializers import ImageSerializer
from wagtail.images.api.v2.views import ImagesAPIViewSet


class ViewSetImageSerializer(ImageSerializer):
    """
    Serializer for images in the /images endpoint.
    """

    rendition_size = "max-900x900"
    jpeg_quality = 60
    webp_quality = 70
    background_colour = "fff"

    def to_representation(self, value):
        representation = super().to_representation(value)
        representation["uuid"] = value.uuid

        image_data = image_generator(
            original_image=value,
            rendition_size=self.rendition_size,
            jpeg_quality=self.jpeg_quality,
            webp_quality=self.webp_quality,
            background_colour=self.background_colour,
        )

        return representation | image_data


class CustomImagesAPIViewSet(ImagesAPIViewSet):
    if settings.WAGTAILAPI_AUTHENTICATION:
        permission_classes = (IsAPITokenAuthenticated,)

    lookup_field = "uuid"
    base_serializer_class = ViewSetImageSerializer
    meta_fields = []
    body_fields = ImagesAPIViewSet.body_fields + [
        "uuid",
        "title",
        "copyright",
        "tags",
        "transcription_heading",
        "transcription",
        "translation_heading",
        "translation",
        "description",
    ]

    def find_object(self, queryset, request):
        if "uuid" in request.GET:
            return queryset.get(uuid=request.GET["uuid"])

    def detail_view(self, request, uuid):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @classmethod
    def get_urlpatterns(cls):
        return [
            path("", cls.as_view({"get": "listing_view"}), name="listing"),
            path("<str:uuid>/", cls.as_view({"get": "detail_view"}), name="detail"),
        ]
