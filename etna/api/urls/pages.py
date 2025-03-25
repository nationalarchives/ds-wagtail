import logging
import time

from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.utils.crypto import constant_time_compare
from rest_framework import status
from rest_framework.response import Response
from wagtail.api.v2.utils import BadRequestError, get_object_detail_url
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Page, PageViewRestriction, Site
from wagtail.search.backends.database.postgres.postgres import PostgresSearchResults

from etna.core.serializers.pages import DefaultPageSerializer

logger = logging.getLogger(__name__)


class CustomPagesAPIViewSet(PagesAPIViewSet):
    known_query_parameters = PagesAPIViewSet.known_query_parameters.union(
        ["password", "author", "include_aliases"]
    )

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

        # TODO: Investigate a way to not use PostgresSearchResults here
        # when using the `?search` parameter (currently throws error)
        if "include_aliases" not in request.GET:
            if not isinstance(queryset, PostgresSearchResults):
                alias_pages = queryset.filter(alias_of_id__isnull=False).values(
                    "id", "alias_of_id"
                )
                original_ids = set(
                    queryset.filter(alias_of_id__isnull=True).values_list(
                        "id", flat=True
                    )
                )
                alias_ids = set(page["id"] for page in alias_pages)
                alias_of_ids = alias_pages.values_list("alias_of_id", flat=True)

                # Exclude any pages with matching alias_of_ids - aliases of the same original page
                for alias_of_id in alias_of_ids:
                    alias_pages_with_same_id = alias_pages.filter(
                        alias_of_id=alias_of_id
                    )
                    if alias_pages_with_same_id.count() > 1:
                        first_page_id = alias_pages_with_same_id.order_by(
                            "depth"
                        ).first()["id"]
                        queryset = queryset.exclude(
                            id__in=alias_pages_with_same_id.values_list(
                                "id", flat=True
                            ).exclude(id=first_page_id)
                        )

                # Exclude any pages that are aliases of pages in the current queryset
                for page in alias_pages:
                    if (
                        page["alias_of_id"] in original_ids
                        or page["alias_of_id"] in alias_ids
                    ):
                        queryset = queryset.exclude(id=page["id"])

        queryset = self.paginate_queryset(queryset)
        serializer = DefaultPageSerializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def detail_view(self, request, pk):
        instance = self.get_object()
        restrictions = instance.get_view_restrictions()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data["meta"].update(
            {
                "breadcrumbs": [
                    {
                        "text": (
                            "Home"
                            if page.url == "/"
                            else page.short_title or page.title
                        ),
                        "href": page.url,
                    }
                    for page in instance.get_ancestors()
                    .order_by("depth")
                    .specific(defer=True)
                    if page.url
                ],
            }
        )
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
            url = url + "?fields=" + request.GET["fields"]

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
        "depth",
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

            path_components = [component for component in path.split("/") if component]

            try:
                page, _, _ = site.root_page.specific.route(request, path_components)
            except Http404:
                return

            if queryset.filter(id=page.id).exists():
                return page

        return super().find_object(queryset, request)
