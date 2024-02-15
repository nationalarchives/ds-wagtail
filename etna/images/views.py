import os

from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404

from wagtail.images.fields import image_format_name_to_content_type
from wagtail.models import Collection

from iiif_prezi3 import Manifest, config

from etna.images.models import CustomImage

config.configs["helpers.auto_fields.AutoLang"].auto_lang = "en"


base_url = settings.WAGTAILADMIN_BASE_URL


def iiif_manifest(_, collection_id: int) -> JsonResponse:
    collection: Collection = get_object_or_404(Collection, pk=collection_id)
    manifest = Manifest(
        id=f"{base_url}/iiif/manifest/{collection_id}",
        label=collection.name,
    )

    for image in CustomImage.objects.filter(collection=collection):
        ext = os.path.splitext(image.file.name)[-1].strip(".")
        mime = image_format_name_to_content_type("jpeg" if ext == "jpg" else ext)
        canvas = manifest.make_canvas(
            id=f"{base_url}/iiif/canvas/{image.id}",
            format=mime,
            height=image.height,
            width=image.width,
        )
        canvas.add_thumbnail(
            image_url=f"{base_url}/iiif/image/{image.id}/full/!300,300/0/default.jpg",
            height=300,
            width=300,
            format="image/jpeg",
        )
        canvas.add_image(
            image_url=f"{base_url}/iiif/image/{image.id}/full/max/0/default.jpg",
            height=image.height,
            width=image.width,
            format="image/jpeg",
        )
    return JsonResponse(data=manifest.jsonld_dict())


def iiif_image_info(_, image_id: int) -> JsonResponse:
    image: CustomImage = get_object_or_404(CustomImage, pk=image_id)

    info = {
        "@context": "http://iiif.io/api/image/2/context.json",
        "@id": f"{base_url}/iiif/image/{image_id}",
        "width": image.width,
        "height": image.height,
        "maxWidth": image.width,
        "maxHeight": image.height,
        "profile": "level0",
    }
    return JsonResponse(data=info)


def iiif_image(
    _, image_id: int, region: str, size: str, rotation: str, quality: str, format: str
) -> StreamingHttpResponse:
    image: CustomImage = get_object_or_404(CustomImage, pk=image_id)
    rendition = image.get_rendition("original|format-jpeg")

    with rendition.get_willow_image() as willow_image:
        mime_type = willow_image.mime_type

    rendition.file.open("rb")
    return StreamingHttpResponse(FileWrapper(rendition.file), content_type=mime_type)
