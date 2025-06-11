from wagtail.api.v2.router import WagtailAPIRouter

from etna.api.urls.blog_posts import BlogPostsAPIViewSet
from etna.api.urls.blogs import BlogsAPIViewSet
from etna.api.urls.events import EventsAPIViewSet
from etna.api.urls.images import CustomImagesAPIViewSet
from etna.api.urls.media import CustomMediaAPIViewSet
from etna.api.urls.page_preview import PagePreviewAPIViewSet
from etna.api.urls.pages import CustomPagesAPIViewSet
from etna.api.urls.redirects import RedirectsAPIViewSet

api_router = WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("pages", CustomPagesAPIViewSet)
api_router.register_endpoint("page_preview", PagePreviewAPIViewSet)
api_router.register_endpoint("images", CustomImagesAPIViewSet)
api_router.register_endpoint("media", CustomMediaAPIViewSet)
api_router.register_endpoint("blogs", BlogsAPIViewSet)
api_router.register_endpoint("blog_posts", BlogPostsAPIViewSet)
api_router.register_endpoint("events", EventsAPIViewSet)
api_router.register_endpoint("redirects", RedirectsAPIViewSet)
