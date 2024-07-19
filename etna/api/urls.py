import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.utils.crypto import constant_time_compare

from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.utils import BadRequestError, get_object_detail_url
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.contrib.redirects.models import Redirect
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.models import Page, PageViewRestriction, Site

from rest_framework import status
from rest_framework.response import Response
from wagtail_headless_preview.models import PagePreview
from wagtailmedia.api.views import MediaAPIViewSet

from etna.core.serializers.pages import DefaultPageSerializer

logger = logging.getLogger(__name__)


class CustomPagesAPIViewSet(PagesAPIViewSet):
    known_query_parameters = PagesAPIViewSet.known_query_parameters.union(["password"])

    def listing_view(self, request):
        queryset = self.get_queryset()

        # Exclude pages that the user doesn't have access to
        restricted_pages = [
            restriction.page
            for restriction in PageViewRestriction.objects.all().select_related("page")
            if not restriction.accept_request(self.request)
        ]

        # Exclude the restricted pages and their descendants from the queryset
        for restricted_page in restricted_pages:
            queryset = queryset.not_descendant_of(restricted_page, inclusive=True)

        self.check_query_parameters(queryset)
        queryset = self.filter_queryset(queryset)
        queryset = self.paginate_queryset(queryset)
        serializer = DefaultPageSerializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def detail_view(self, request, pk):
        instance = self.get_object()
        restrictions = instance.get_view_restrictions()
        serializer = self.get_serializer(instance)
        data = serializer.data
        if not restrictions:
            return Response(data)
        restricted_data = {
            "id": data["id"],
            "meta": {"privacy": data["meta"]["privacy"], "locked": True},
        }
        for restriction in restrictions:
            if restriction.restriction_type == PageViewRestriction.PASSWORD:
                if "password" in request.GET:
                    if constant_time_compare(
                        request.GET["password"], restriction.password
                    ):
                        return Response(data)
                    else:
                        data = restricted_data | {"message": "Incorrect password."}
                        return Response(data)
                else:
                    data = restricted_data | {
                        "message": "Password required to view this resource.",
                    }
                    return Response(data)
        data = restricted_data | {
            "message": "Selected privacy mode is not compatible with this API.",
        }
        return Response(data, status=status.HTTP_403_FORBIDDEN)

    def find_view(self, request):
        queryset = self.get_queryset()

        try:
            obj = self.find_object(queryset, request)
            if obj is None:
                raise self.model.DoesNotExist

        except self.model.DoesNotExist:
            raise Http404("not found")

        url = get_object_detail_url(
            self.request.wagtailapi_router, request, self.model, obj.pk
        )
        if url is None:
            raise Exception(
                "Cannot generate URL to detail view. Is '{}' installed in the API router?".format(
                    self.__class__.__name__
                )
            )

        if "fields" in request.GET:
            url = url + "fields=" + request.GET["fields"]

        return redirect(url)

    def get_base_queryset(self):
        """
        Copy of https://github.com/wagtail/wagtail/blob/f5552c40442b0ed6a0316ee899c7f28a0b1ed4e5/wagtail/api/v2/views.py#L491
        that doesn't remove restricted pages
        """

        request = self.request

        # Get all live pages
        queryset = Page.objects.all().live()

        # Check if we have a specific site to look for
        if "site" in request.GET:
            # Optionally allow querying by port
            if ":" in request.GET["site"]:
                (hostname, port) = request.GET["site"].split(":", 1)
                query = {
                    "hostname": hostname,
                    "port": port,
                }
            else:
                query = {
                    "hostname": request.GET["site"],
                }
            try:
                site = Site.objects.get(**query)
            except Site.MultipleObjectsReturned:
                raise BadRequestError(
                    "Your query returned multiple sites. Try adding a port number to your site filter."
                )
        else:
            # Otherwise, find the site from the request
            site = Site.find_for_request(self.request)

        if site:
            base_queryset = queryset
            queryset = base_queryset.descendant_of(site.root_page, inclusive=True)

            # If internationalisation is enabled, include pages from other language trees
            if getattr(settings, "WAGTAIL_I18N_ENABLED", False):
                for translation in site.root_page.get_translations():
                    queryset |= base_queryset.descendant_of(translation, inclusive=True)

        else:
            # No sites configured
            queryset = queryset.none()

        return queryset

    meta_fields = PagesAPIViewSet.meta_fields + [
        "privacy",
        "last_published_at",
        "url",
    ]

    def find_object(self, queryset, request):
        site = Site.find_for_request(request)
        if "html_path" in request.GET and site is not None:
            path = request.GET["html_path"]

            redirect_queryset = Redirect.objects.all()
            redirects = redirect_queryset.filter(
                Q(old_path=path)
                | Q(old_path=path.strip("/"))
                | Q(old_path=f"/{path.strip('/')}")
                | Q(old_path=f"{path.strip('/')}/")
                | Q(old_path=f"/{path.strip('/')}/")
            )
            if redirects.exists():
                if redirects.get().redirect_page:
                    if new_path := redirects.get().redirect_page.url:
                        logger.info(f"Redirect detected: {path} ---> {new_path}")
                        path = new_path
                # elif redirects.get().redirect_link:
                #     if new_path := redirects.get().redirect_link:
                #         logger.info(f"Redirect detected: {path} ---> {new_path}")
                #         path = new_path

            path_components = [component for component in path.split("/") if component]

            try:
                page, _, _ = site.root_page.specific.route(request, path_components)
            except Http404:
                return

            if queryset.filter(id=page.id).exists():
                return page

        return super().find_object(queryset, request)


class PagePreviewAPIViewSet(PagesAPIViewSet):
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

        page_preview = PagePreview.objects.get(
            content_type=content_type, token=self.request.GET["token"]
        )
        page = page_preview.as_page()
        if not page.pk:
            # fake primary key to stop API URL routing from complaining
            page.pk = 0

        return page


class CustomImagesAPIViewSet(ImagesAPIViewSet):
    body_fields = ImagesAPIViewSet.body_fields + [
        "title",
        "file",
        "copyright",
        "is_sensitive",
        "custom_sensitive_image_warning",
        "tags",
        "transcription_heading",
        "transcription",
        "translation_heading",
        "translation",
        "record",
        "record_dates",
        "description",
    ]


api_router = WagtailAPIRouter("wagtailapi")

api_router.register_endpoint("pages", CustomPagesAPIViewSet)
api_router.register_endpoint("page_preview", PagePreviewAPIViewSet)
api_router.register_endpoint("images", CustomImagesAPIViewSet)
api_router.register_endpoint("media", MediaAPIViewSet)
