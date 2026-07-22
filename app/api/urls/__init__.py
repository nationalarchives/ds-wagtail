from wagtail.api.v2.router import WagtailAPIRouter

from app.api.urls.blog_posts import BlogPostsAPIViewSet
from app.api.urls.blogs import BlogsAPIViewSet
from app.api.urls.catalogue import CatalogueAPIViewSet
from app.api.urls.education import (
    EducationResourcesAPIViewSet,
    EducationSessionsAPIViewSet,
)
from app.api.urls.events import EventsAPIViewSet
from app.api.urls.foi import FreedomOfInformationRequestsAPIViewSet
from app.api.urls.globals import GlobalsAPIViewSet
from app.api.urls.images import CustomImagesAPIViewSet
from app.api.urls.media import CustomMediaAPIViewSet
from app.api.urls.page_preview import PagePreviewAPIViewSet
from app.api.urls.pages import CustomPagesAPIViewSet
from app.api.urls.redirects import RedirectsAPIViewSet
from app.api.urls.external_applications import ExternalApplicationPagesAPIViewSet
from app.api.urls.unified_search import UnifiedSearchAPIViewSet
from app.api.urls.tags import ArticleTagsAPIViewSet

api_router = WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("pages", CustomPagesAPIViewSet)
api_router.register_endpoint("education/resources", EducationResourcesAPIViewSet)
api_router.register_endpoint("education/sessions", EducationSessionsAPIViewSet)
api_router.register_endpoint("page_preview", PagePreviewAPIViewSet)
api_router.register_endpoint("article_tags", ArticleTagsAPIViewSet)
api_router.register_endpoint("images", CustomImagesAPIViewSet)
api_router.register_endpoint("media", CustomMediaAPIViewSet)
api_router.register_endpoint("blogs", BlogsAPIViewSet)
api_router.register_endpoint("blog_posts", BlogPostsAPIViewSet)
api_router.register_endpoint("events", EventsAPIViewSet)
api_router.register_endpoint("redirects", RedirectsAPIViewSet)
api_router.register_endpoint("foi", FreedomOfInformationRequestsAPIViewSet)
api_router.register_endpoint("catalogue", CatalogueAPIViewSet)
api_router.register_endpoint("globals", GlobalsAPIViewSet)
api_router.register_endpoint("external_applications", ExternalApplicationPagesAPIViewSet)
api_router.register_endpoint("search", UnifiedSearchAPIViewSet)
