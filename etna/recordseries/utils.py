from typing import Literal, NotRequired, TypedDict
from urllib.parse import urlencode, urlunsplit

from django.urls import reverse

from .models import RecordSeries


class SeriesSearchQuery(TypedDict):
    group: NotRequired[Literal["digitised"]]


def get_series_search_results_url(
    record_series: RecordSeries,
) -> str:
    search_url = reverse("search-catalogue")
    query_dict: SeriesSearchQuery = {}

    # TODO: Add a query parameter to filter by the series once that is in place.
    #       e.g.  query_dict["series"] = series.ciim_series_identifier

    if record_series.show_only_digitised_records:
        query_dict["group"] = "digitised"
    query = urlencode(query_dict)
    return urlunsplit(
        (
            "",
            "",
            search_url,
            query,
            "",
        )
    )
