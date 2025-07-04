from wagtail.api.v2.router import WagtailAPIRouter

from app.api.urls.blog_posts import BlogPostsAPIViewSet
from app.api.urls.blogs import BlogsAPIViewSet
from app.api.urls.events import EventsAPIViewSet
from app.api.urls.images import CustomImagesAPIViewSet
from app.api.urls.media import CustomMediaAPIViewSet
from app.api.urls.page_preview import PagePreviewAPIViewSet
from app.api.urls.pages import CustomPagesAPIViewSet
from app.api.urls.redirects import RedirectsAPIViewSet

api_router = WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("pages", CustomPagesAPIViewSet)
api_router.register_endpoint("page_preview", PagePreviewAPIViewSet)
api_router.register_endpoint("images", CustomImagesAPIViewSet)
api_router.register_endpoint("media", CustomMediaAPIViewSet)
api_router.register_endpoint("blogs", BlogsAPIViewSet)
api_router.register_endpoint("blog_posts", BlogPostsAPIViewSet)
api_router.register_endpoint("events", EventsAPIViewSet)
api_router.register_endpoint("redirects", RedirectsAPIViewSet)
