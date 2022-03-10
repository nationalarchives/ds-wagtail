from django.core.paginator import Page
from django.shortcuts import render

from ..ciim.client import Aggregation, Template
from ..ciim.paginator import APIPaginator
from ..records.models import Record
from .forms import SearchForm


def catalogue_search(request):

    per_page = int(request.GET.get("per_page", 20))
    page_number = int(request.GET.get("page", 1))
    offset = (page_number - 1) * per_page

    bucket_count_response = {}
    records = []
    count = 0

    data = request.GET.copy()
    data.setdefault("group", "group:tna")
    form = SearchForm(data)

    if form.is_valid():
        # If no keyword is provided, pass None to client to fetch all results.
        keyword = form.cleaned_data.get("keyword")
        # If no filter_keyword is provided, pass None to client bypass search within
        filter_keyword = form.cleaned_data.get("filter_keyword")
        filter_aggregations = form.cleaned_data.get("filter_aggregations")

        response = Record.api.client.search(
            template=Template.DETAILS,
            keyword=keyword,
            filter_keyword=filter_keyword,
            filter_aggregations=filter_aggregations,
            aggregations=[
                Aggregation.CATALOGUE_SOURCE,
                Aggregation.CLOSURE,
                Aggregation.COLLECTION,
                Aggregation.GROUP,
                Aggregation.LEVEL,
                Aggregation.TOPIC,
            ],
            offset=offset,
            size=per_page,
        )
        bucket_count_response, result_response = response["responses"]
        records = result_response["hits"]["hits"]
        count = result_response["hits"]["total"]["value"]

        form.update_from_response(response=result_response)

    paginator = APIPaginator(count, per_page=per_page)
    page = Page(records, number=page_number, paginator=paginator)
    page_range = paginator.get_elided_page_range(number=page_number, on_ends=0)

    return render(
        request,
        "search/catalogue_search.html",
        {
            "page": page,
            "page_range": page_range,
            "form": form,
            "bucket_count_response": bucket_count_response,
        },
    )
