import logging

from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.utils.crypto import constant_time_compare
from rest_framework import status
from rest_framework.response import Response
from wagtail.api.v2.filters import (
    AncestorOfFilter,
    ChildOfFilter,
    DescendantOfFilter,
    FieldsFilter,
    LocaleFilter,
    OrderingFilter,
    SearchFilter,
    TranslationOfFilter,
)
from wagtail.api.v2.utils import BadRequestError, get_object_detail_url
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Page, PageViewRestriction, Site

from etna.core.serializers.pages import DefaultPageSerializer

from ..filters import AliasFilter, DescendantOfPathFilter, SiteFilter

logger = logging.getLogger(__name__)


class CustomPagesAPIViewSet(PagesAPIViewSet):
    known_query_parameters = PagesAPIViewSet.known_query_parameters.union(
        ["password", "author", "include_aliases", "descendant_of_path"]
    )

    # TODO: Remove this when Wagtail is updated
    # https://github.com/wagtail/wagtail/pull/12141
    find_query_parameters = [
        "id",
        "html_path",
    ]

    # Copied from wagtail.api.v2.views.PagesAPIViewSet
    # to allow insertion of AliasFilter before SearchFilter
    filter_backends = [
        FieldsFilter,
        ChildOfFilter,
        AncestorOfFilter,
        DescendantOfFilter,
        DescendantOfPathFilter,
        OrderingFilter,
        TranslationOfFilter,
        LocaleFilter,
        SiteFilter,
        AliasFilter,  # Needs to come before SearchFilter
        SearchFilter,  # Needs to be last, as SearchResults querysets cannot be filtered further
    ]

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

        if "author" in request.GET and request.GET["author"]:
            queryset = queryset.filter(author_tags__author=request.GET["author"])

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
        breadcrumbs = [
            {
                "text": ("Home" if page.url == "/" else page.short_title or page.title),
                "href": page.url,
            }
            for page in instance.get_ancestors().order_by("depth").specific(defer=True)
            if page.url
        ]
        if "meta" in data:
            data["meta"].update(
                {
                    "breadcrumbs": breadcrumbs,
                }
            )
        else:
            data["meta"] = {
                "breadcrumbs": breadcrumbs,
            }
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

    # TODO: Can be removed when Wagtail is updated
    # https://github.com/wagtail/wagtail/pull/12141
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

        # Retain all query parameters except ones only used to find the object
        query = request.GET.copy()
        for param in self.find_query_parameters:
            query.pop(param, None)

        return redirect(f"{url}?{query.urlencode()}")

    def get_base_queryset(self):
        """
        Copy of https://github.com/wagtail/wagtail/blob/f5552c40442b0ed6a0316ee899c7f28a0b1ed4e5/wagtail/api/v2/views.py#L491
        that doesn't remove restricted pages - we use this to expose all pages which
        allows us to render password-protected pages in the frontend.
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
        "depth",
    ]

    def find_object(self, queryset, request):
        if "site" in request.GET:
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
            site = Site.find_for_request(self.request)

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

            path_components = [component for component in path.split("/") if component]

            try:
                page, _, _ = site.root_page.specific.route(request, path_components)
            except Http404:
                return

            if queryset.filter(id=page.id).exists():
                return page

        return super().find_object(queryset, request)
