from ninja import Schema
from wagtail.api.v3.registry import registry
from wagtail.api.v3.schemas import PageSchema, read_generator
from wagtail.api.v3.schemas.pages import PageMetaSchema
from wagtail.models import AbstractPage, get_page_models

from app.core.models.basepage import BasePage
from app.core.models.mixins import SocialMixin


def _serializer_for(api_fields, field_name):
    """Return the serializer bound to a model's APIField of the given name."""
    return next(f.serializer for f in api_fields if f.name == field_name)


def _image_serializer_for(obj: AbstractPage, field_name: str, fallback):
    """Return the concrete page's serializer for an image metadata field."""
    try:
        return _serializer_for(obj.api_meta_fields, field_name)
    except StopIteration:
        return fallback


# Reuse the exact serializer instances declared on each model's APIFields, so
# rendition sizes stay in sync with API v2 (app/core/models/basepage.py,
# app/core/models/mixins.py) rather than being duplicated here.
_teaser_image_serializer = BasePage._teaser_image_api_field.serializer
_search_image_serializer = _serializer_for(
    SocialMixin._social_base_api_meta_fields, "search_image"
)
_twitter_og_image_serializer = _serializer_for(
    SocialMixin._social_base_api_meta_fields, "twitter_og_image"
)


class ImageRenditionSchema(Schema):
    url: str
    full_url: str
    width: int
    height: int


ImageSchema = dict[str, int | str | ImageRenditionSchema]


def _serialize_image(serializer, image) -> dict | None:
    """Render an image through the given serializer, coercing its uuid to a
    plain string - the model field is a UUID instance, which DRF's JSON
    renderer stringifies but Pydantic's strict schema validation won't."""
    representation = serializer.to_representation(image)
    if representation is not None:
        representation["uuid"] = str(representation["uuid"])
    return representation


class SitePageMetaSchema(PageMetaSchema):
    """Metadata shared by the page types exposed by the site API."""

    page_path: str | None = None
    url: str | None = None
    full_url: str | None = None
    privacy: str | None = None
    teaser_text: str | None = None
    breadcrumbs: list[dict[str, str]] | None = None
    published_date: str | None = None
    depth: int | None = None
    last_published_at: str | None = None
    search_image: ImageSchema | None = None
    teaser_image: ImageSchema | None = None
    twitter_og_description: str | None = None
    twitter_og_image: ImageSchema | None = None
    twitter_og_title: str | None = None

    @staticmethod
    def resolve_page_path(obj: AbstractPage, context: dict) -> str | None:
        return getattr(obj, "page_path", None)

    @staticmethod
    def resolve_url(obj: AbstractPage, context: dict) -> str | None:
        return getattr(obj, "url", None)

    @staticmethod
    def resolve_full_url(obj: AbstractPage, context: dict) -> str | None:
        return getattr(obj, "full_url", None)

    @staticmethod
    def resolve_privacy(obj: AbstractPage, context: dict) -> str | None:
        return getattr(obj, "privacy", None)

    @staticmethod
    def resolve_published_date(obj: AbstractPage, context: dict) -> str | None:
        value = getattr(obj, "published_date", None)
        return value.isoformat() if value else None

    @staticmethod
    def resolve_last_published_at(obj: AbstractPage, context: dict) -> str | None:
        value = getattr(obj, "last_published_at", None)
        return value.isoformat() if value else None

    @staticmethod
    def resolve_search_image(
        obj: AbstractPage, context: dict
    ) -> ImageSchema | None:
        return _serialize_image(
            _image_serializer_for(obj, "search_image", _search_image_serializer),
            getattr(obj, "search_image", None),
        )

    @staticmethod
    def resolve_teaser_image(
        obj: AbstractPage, context: dict
    ) -> ImageSchema | None:
        return _serialize_image(
            _image_serializer_for(obj, "teaser_image", _teaser_image_serializer),
            getattr(obj, "teaser_image", None),
        )

    @staticmethod
    def resolve_twitter_og_image(
        obj: AbstractPage, context: dict
    ) -> ImageSchema | None:
        return _serialize_image(
            _image_serializer_for(
                obj, "twitter_og_image", _twitter_og_image_serializer
            ),
            getattr(obj, "twitter_og_image", None),
        )


class SitePageSchema(PageSchema):
    meta: SitePageMetaSchema


def register_page_schemas() -> None:
    """
    Replace each page model's registered read schema with one based on
    ``SitePageSchema``.

    Must run from ``ApiAppConfig.ready()`` rather than from ``app.api.v3.api``:
    several wagtail apps (``wagtail.images``, ``wagtail.snippets``, ``wagtail.
    contrib.redirects``, ...) import ``wagtail.api.v3.api`` from their own
    ``ready()`` to attach their routers, and that import pulls in
    ``wagtail.api.v3.routers.pages`` - which reads this registry to build its
    ``PageDetailSchema`` union at *import* time. Since ``app.api`` is listed
    before those apps in ``INSTALLED_APPS``, running this from its ``ready()``
    guarantees the registry is patched before anything imports
    ``wagtail.api.v3.routers.pages`` for the first time. Patching the registry
    from ``app.api.v3.api`` (which is only imported later, from ``config.
    urls``) is too late - that module has already been built with the
    original schemas by then.
    """
    for model in get_page_models():
        registration = registry.get(model._meta.label)
        if registration is not None:
            registration.read_schema = read_generator.generate_schema(
                model, base_class=SitePageSchema
            )
