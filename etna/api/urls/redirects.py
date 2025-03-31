from rest_framework.response import Response
from wagtail.api.v2.views import BaseAPIViewSet
from wagtail.contrib.redirects.models import Redirect

from etna.core.serializers.redirects import RedirectSerializer


class RedirectsAPIViewSet(BaseAPIViewSet):
    model = Redirect

    def listing_view(self, request):
        queryset = self.get_queryset()
        self.check_query_parameters(queryset)
        queryset = self.filter_queryset(queryset)
        queryset = self.paginate_queryset(queryset)
        serializer = RedirectSerializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def detail_view(self, request, pk):
        instance = self.get_object()
        serializer = RedirectSerializer(instance)
        return Response(serializer.data)

    def find_object(self, queryset, request):
        if "path" in request.GET:
            # Taken from https://github.com/wagtail/wagtail/blob/main/wagtail/contrib/redirects/models.py#L165-L169
            path = request.GET["path"]
            path = path.strip()
            if not path.startswith("/"):
                path = "/" + path
            if path.endswith("/") and len(path) > 1:
                path = path[:-1]
            return queryset.get(old_path=path)
