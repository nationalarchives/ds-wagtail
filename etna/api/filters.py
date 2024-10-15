import datetime

from wagtail.api.v2.utils import BadRequestError

from rest_framework.filters import BaseFilterBackend


class PublishedDateFilter(BaseFilterBackend):
    """
    Implements the ?year, ?month and ?day filters to filter the results to only
    contain blog posts that were published in the specified year/month/day.
    """

    def filter_queryset(self, request, queryset, view):
        if "day" in request.GET and (
            "year" not in request.GET or "month" not in request.GET
        ):
            raise BadRequestError(
                "cannot use day filter without a year and month filter"
            )
        if "month" in request.GET and "year" not in request.GET:
            raise BadRequestError("cannot use month filter without a year filter")

        if "year" in request.GET:
            try:
                year = int(request.GET["year"])
                if year < 0:
                    raise ValueError()
            except ValueError:
                raise BadRequestError("year must be a positive integer")
            queryset = queryset.filter(**{"published_date__year": year})

            if "month" in request.GET:
                try:
                    month = int(request.GET["month"])
                    if month < 0 or month > 12:
                        raise ValueError()
                except ValueError:
                    raise BadRequestError(
                        "month must be a positive integer between 1-12"
                    )
                queryset = queryset.filter(**{"published_date__month": month})

                if "day" in request.GET:
                    try:
                        day = int(request.GET["day"])
                        datetime.datetime(year, month, day)
                    except ValueError:
                        raise BadRequestError(
                            f"{year}-{month}-{day} is not a valid date"
                        )
                    queryset = queryset.filter(**{"published_date__day": day})

        return queryset
