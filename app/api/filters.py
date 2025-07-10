import datetime

from rest_framework.filters import BaseFilterBackend
from wagtail.api.v2.utils import BadRequestError
from wagtail.models import Page, Site
from wagtail.search.backends.database.postgres.postgres import PostgresSearchResults


class PublishedDateFilter(BaseFilterBackend):
    """
    Implements the ?year, ?month and ?day filters to filter the results to only
    contain blog posts that were published in the specified year/month/day.
    """

    def filter_queryset(self, request, queryset, view):
        self.validate_date_filters(request)

        if "year" in request.GET:
            year = self.get_year(request)
            queryset = queryset.filter(**{"published_date__year": year})

            if "month" in request.GET:
                month = self.get_month(request)
                queryset = queryset.filter(**{"published_date__month": month})

                if "day" in request.GET:
                    day = self.get_day(request, year, month)
                    queryset = queryset.filter(**{"published_date__day": day})

        return queryset

    def validate_date_filters(self, request):
        if "day" in request.GET and (
            "year" not in request.GET or "month" not in request.GET
        ):
            raise BadRequestError(
                "cannot use day filter without a year and month filter"
            )
        if "month" in request.GET and "year" not in request.GET:
            raise BadRequestError("cannot use month filter without a year filter")

    def get_year(self, request):
        try:
            year = int(request.GET["year"])
            if year < 0:
                raise ValueError()
        except ValueError:
            raise BadRequestError("year must be a positive integer")
        return year

    def get_month(self, request):
        try:
            month = int(request.GET["month"])
            if month < 1 or month > 12:
                raise ValueError()
        except ValueError:
            raise BadRequestError("month must be a positive integer between 1-12")
        return month

    def get_day(self, request, year, month):
        try:
            day = int(request.GET["day"])
            datetime.datetime(year, month, day)
        except ValueError:
            raise BadRequestError(f"{year}-{month}-{day} is not a valid date")
        return day


class AuthorFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if "author" in request.GET:
            try:
                author = request.GET["author"]
                if not author:
                    raise ValueError()
            except ValueError:
                raise BadRequestError("you must provide an author name")
            queryset = queryset.filter(**{"author_tags__author__slug": author})
        return queryset


class AliasFilter(BaseFilterBackend):
    """
    Filter to remove aliases from the queryset.
    This needs to go after all other filters, and before the SearchFilter, as
    SearchResults querysets are not filterable.
    """

    def filter_queryset(self, request, queryset, view):
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
        return queryset


class SiteFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
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
            # site = Site.find_for_request(request)

            # Otherwise, use the default site
            site = Site.objects.get(is_default_site=True)

        if site:
            base_queryset = queryset
            queryset = base_queryset.descendant_of(site.root_page, inclusive=True)

        else:
            # No sites configured
            queryset = queryset.none()

        return queryset


class DescendantOfPathFilter(BaseFilterBackend):
    """
    Implements the ?descendant_of filter which limits the set of pages to a
    particular branch of the page tree.
    """

    def filter_queryset(self, request, queryset, view):
        if "descendant_of_path" in request.GET:
            if hasattr(queryset, "_filtered_by_child_of"):
                raise BadRequestError(
                    "filtering by descendant_of_path with child_of is not supported"
                )
            try:
                parent_page_path = request.GET["descendant_of_path"]
                if parent_page_path == "/":
                    parent_page = view.get_root_page()
                else:
                    path_components = [
                        component
                        for component in parent_page_path.split("/")
                        if component
                    ]
                    site = Site.find_for_request(request)
                    try:
                        parent_page, _, _ = site.root_page.specific.route(
                            request, path_components
                        )
                    except Exception:
                        raise BadRequestError("ancestor page doesn't exist")
            except Page.DoesNotExist:
                raise BadRequestError("ancestor page doesn't exist")

            queryset = queryset.descendant_of(parent_page)

        return queryset


class LocationFilter(BaseFilterBackend):
    """
    Implements the ?online and ?at_tna filter which limits the set of pages to a
    particular location.
    """

    def filter_queryset(self, request, queryset, view):
        if "online" in request.GET:
            return queryset.filter(location__online=True)
        elif "at_tna" in request.GET:
            return queryset.filter(location__at_tna=True)
        return queryset


class EventDateFilter(BaseFilterBackend):
    """
    Implements the ?from and ?to filters to filter events by their start and/or end dates.

    The dates are inclusive, meaning that events starting or ending on the specified dates will be included.

    The filtering logic is as follows:

    1. If both 'from' and 'to' are provided:

                     FROM...............TO
                     |                   |
    ░░░░░EVENT░░░░░  |                   |                    Not included
              ░░░░░EVENT░░░░░            |                    Included
                     |  ░░░░░EVENT░░░░░  |                    Included
                  ░░░░░░░░░░░EVENT░░░░░░░░░░░                 Included
                     |            ░░░░░EVENT░░░░░             Included
                     |                   |  ░░░░░EVENT░░░░░   Not included


    2. If only 'from' is provided:

                     FROM.................
                     |
    ░░░░░EVENT░░░░░  |                                        Not included
              ░░░░░EVENT░░░░░                                 Included
                     |  ░░░░░EVENT░░░░░                       Included


    3. If only 'to' is provided:

                     ...................TO
                                         |
                        ░░░░░EVENT░░░░░  |                    Included
                                  ░░░░░EVENT░░░░░             Included
                                         |  ░░░░░EVENT░░░░░   Not included

    """

    def filter_queryset(self, request, queryset, view):
        if "from" in request.GET:
            try:
                from_date = datetime.datetime.fromisoformat(request.GET["from"])
            except ValueError:
                raise BadRequestError(
                    "Invalid date format for 'from' filter. Use ISO format (YYYY-MM-DD)."
                )
        else:
            from_date = None

        if "to" in request.GET:
            try:
                to_date = datetime.datetime.fromisoformat(request.GET["to"])
            except ValueError:
                raise BadRequestError(
                    "Invalid date format for 'to' filter. Use ISO format (YYYY-MM-DD)."
                )
        else:
            to_date = None

        if from_date and to_date and from_date > to_date:
            raise BadRequestError("'from' date cannot be after 'to' date.")

        if from_date:
            queryset = queryset.filter(end_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(start_date__lte=to_date)

        return queryset
