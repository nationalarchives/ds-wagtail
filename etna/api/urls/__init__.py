from wagtail.api.v2.router import WagtailAPIRouter
from wagtailmedia.api.views import MediaAPIViewSet

from .blog_posts import BlogPostsAPIViewSet
from .blogs import BlogsAPIViewSet
from .images import CustomImagesAPIViewSet
from .page_preview import PagePreviewAPIViewSet
from .pages import CustomPagesAPIViewSet
from .redirects import RedirectsAPIViewSet
from .events import EventPagesAPIViewSet

api_router = WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("pages", CustomPagesAPIViewSet)
api_router.register_endpoint("page_preview", PagePreviewAPIViewSet)
api_router.register_endpoint("images", CustomImagesAPIViewSet)
api_router.register_endpoint("media", MediaAPIViewSet)
api_router.register_endpoint("blogs", BlogsAPIViewSet)
api_router.register_endpoint("blog_posts", BlogPostsAPIViewSet)
api_router.register_endpoint("redirects", RedirectsAPIViewSet)
api_router.register_endpoint("events", EventPagesAPIViewSet)
