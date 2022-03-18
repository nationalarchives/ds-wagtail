from django.core.paginator import Page
from django.shortcuts import render

from ..ciim.client import Aggregation, DateField, SortOrder, Stream, Template
from ..ciim.paginator import APIPaginator
from ..records.models import Record
from .forms import CatalogueSearchForm, FeaturedSearchForm, WebsiteSearchForm

# Aggregations and their headings, passed /searchAll to fetch
# counts and output along with grouped results.
FEATURED_BUCKETS = [
    {
        "aggregation": "group:tna",
        "heading": "Records from The National Archives",
    },
    {
        "aggregation": "group:nonTna",
        "heading": "Records from other UK archives",
    },
    {
        "aggregation": "group:blog",
        "heading": "Blog",
    },
    {
        "aggregation": "group:researchGuide",
        "heading": "Research Guides",
    },
]


def featured_search(request):

    responses = []

    form = FeaturedSearchForm(request.GET)

    if form.is_valid():
        q = form.cleaned_data.get("q")

        response = Record.api.client.search_all(
            q=q,
            filter_aggregations=[b["aggregation"] for b in FEATURED_BUCKETS],
            size=3,
        )
        responses = response.get("responses", [])

    # Combine bucket and responses to output headings and results together
    responses = zip(responses, FEATURED_BUCKETS)

    return render(
        request,
        "search/featured_search.html",
        {
            "form": form,
            "responses": responses,
        },
    )


def search(request):
    form = CatalogueSearchForm()

    # Make empty search to fetch aggregations
    response = Record.api.client.search(
        template=Template.DETAILS,
        aggregations=[
            Aggregation.CATALOGUE_SOURCE,
            Aggregation.CLOSURE,
            Aggregation.COLLECTION,
            Aggregation.GROUP,
            Aggregation.LEVEL,
            Aggregation.TOPIC,
        ],
        size=0,
    )
    bucket_count_response, _ = response["responses"]

    return render(
        request,
        "search/search.html",
        {
            "form": form,
            "bucket_count_response": bucket_count_response,
        },
    )


def catalogue_search(request):

    per_page = int(request.GET.get("per_page", 20))
    page_number = int(request.GET.get("page", 1))
    offset = (page_number - 1) * per_page

    bucket_count_response = {}
    records = []
    count = 0

    data = request.GET.copy()
    data.setdefault("group", "group:tna")
    form = CatalogueSearchForm(data)

    if form.is_valid():
        q = form.cleaned_data.get("q")
        filter_keyword = form.cleaned_data.get("filter_keyword")
        filter_aggregations = form.cleaned_data.get("filter_aggregations")

        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")

        sort_by = form.cleaned_data.get("sort_by")

        response = Record.api.client.search(
            template=Template.DETAILS,
            q=q,
            filter_keyword=filter_keyword,
            filter_aggregations=filter_aggregations,
            stream=Stream.EVIDENTIAL,
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
            start_date=start_date,
            end_date=end_date,
            date_field=DateField.DATE_OPENING,
            sort_by=sort_by,
            sort_order=SortOrder.ASC,
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


def website_search(request):

    per_page = int(request.GET.get("per_page", 20))
    page_number = int(request.GET.get("page", 1))
    offset = (page_number - 1) * per_page

    bucket_count_response = {}
    records = []
    count = 0

    data = request.GET.copy()
    data.setdefault("group", "group:blog")

    form = WebsiteSearchForm(data)
    if form.is_valid():
        q = form.cleaned_data.get("q")
        filter_keyword = form.cleaned_data.get("filter_keyword")
        filter_aggregations = form.cleaned_data.get("filter_aggregations")

        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")

        sort_by = form.cleaned_data.get("sort_by")

        response = Record.api.client.search(
            template=Template.DETAILS,
            q=q,
            filter_keyword=filter_keyword,
            filter_aggregations=filter_aggregations,
            stream=Stream.INTERPRETIVE,
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
            start_date=start_date,
            end_date=end_date,
            date_field=DateField.DATE_OPENING,
            sort_by=sort_by,
            sort_order=SortOrder.ASC,
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
        "search/website_search.html",
        {
            "page": page,
            "page_range": page_range,
            "form": form,
            "bucket_count_response": bucket_count_response,
        },
    )
