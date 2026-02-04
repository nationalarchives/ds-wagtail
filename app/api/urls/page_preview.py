from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from wagtail.api.v2.utils import BadRequestError
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail_headless_preview.models import PagePreview

from app.api.permissions import IsAPITokenAuthenticated
from django.conf import settings



class PagePreviewAPIViewSet(PagesAPIViewSet):
    if settings.WAGTAILAPI_AUTHENTICATION:
        permission_classes = (
            IsAPITokenAuthenticated,
        )

    known_query_parameters = PagesAPIViewSet.known_query_parameters.union(
        ["content_type", "token"]
    )

    def listing_view(self, request):
        page = self.get_object()
        serializer = self.get_serializer(page)
        return Response(serializer.data)

    def detail_view(self, request, pk):
        page = self.get_object()
        serializer = self.get_serializer(page)
        return Response(serializer.data)

    def get_object(self):
        if "content_type" not in self.request.GET:
            raise BadRequestError("content_type not specified")
        if "token" not in self.request.GET:
            raise BadRequestError("token not specified")

        app_label, model = self.request.GET["content_type"].split(".")
        content_type = ContentType.objects.get(app_label=app_label, model=model)

        try:
            page_preview = PagePreview.objects.get(
                content_type=content_type, token=self.request.GET["token"]
            )
        except PagePreview.DoesNotExist:
            raise BadRequestError("Page preview does not exist")
        page = page_preview.as_page()
        if not page.pk:
            # fake primary key to stop API URL routing from complaining
            page.pk = 0

        return page
