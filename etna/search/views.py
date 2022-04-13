from typing import Any, Dict, List

from django.core.paginator import Page
from django.forms import Form
from django.http import Http404
from django.shortcuts import render

from wagtail.core.utils import camelcase_to_underscore

from ..ciim.client import Aggregation, SortOrder, Stream, Template
from ..ciim.constants import CATALOGUE_BUCKETS, FEATURED_BUCKETS, WEBSITE_BUCKETS
from ..ciim.paginator import APIPaginator
from ..records.models import Record
from .forms import CatalogueSearchForm, FeaturedSearchForm, WebsiteSearchForm


def underscore_to_camelcase(word, lower_first=True):
    result = "".join(char.capitalize() for char in word.split("_"))
    if lower_first:
        result = result[0].lower() + result[1:]
    return result


def get_api_filters_from_form_values(form: Form) -> List[str]:
    """
    The API expects filter values to be supplied in a certain way: as a list
    of strings prefixed with the API field name. This function takes care
    of matching up form fields to the relevant API field name, and returning
    a list of filter strings that the API will understand.

    Ideally, this function would be a method on class-based view that all
    of the search views inherited from.
    """
    filter_aggregations = []
    for field_name in form.dynamic_choice_fields:
        filter_name = underscore_to_camelcase(field_name)
        value = form.cleaned_data.get(field_name)
        filter_aggregations.extend((f"{filter_name}:{v}" for v in value))

    # The 'group' field is handled separately, as it only returns a single value
    filter_aggregations.append(f"group:{form.cleaned_data['group']}")
    return filter_aggregations


def update_field_choices_to_refelect_api_response(
    form: Form, aggregations: Dict[str, Dict[str, Any]]
):
    """
    Search forms contain special multiple choice fields, whose 'choice'
    values are updated to reflect aggregated 'bucket' values included in
    the API response. This method finds the relevant fields based on
    the API value and triggers that update for each field.

    This updated is done for two reasons:

    1. To filter out options that are not relevant to the result
    2. To include document counts in the choice labels.

    Ideally, this function would be a method on class-based view that all
    of the search views inherited from.
    """

    for key, value in aggregations.items():
        if buckets := value.get("buckets"):
            field_name = camelcase_to_underscore(key)
            if field_name in form.dynamic_choice_fields:
                form.fields[field_name].update_choices(buckets)
                form[field_name].more_filter_options_available = bool(
                    value.get("sum_other_doc_count", 0)
                )


def featured_search(request):

    responses = []

    form = FeaturedSearchForm(request.GET)

    if form.is_valid():
        q = form.cleaned_data.get("q")

        response = Record.api.client.search_all(
            q=q,
            filter_aggregations=[f"group:{bucket.key}" for bucket in FEATURED_BUCKETS],
            size=3,
        )
        responses = response.get("responses", [])

    result_groups = {}
    for i, bucket in enumerate(FEATURED_BUCKETS):
        result_groups[bucket.key] = responses[i]
        result_groups[bucket.key]["bucket"] = bucket

    return render(
        request,
        "search/featured_search.html",
        {
            "form": form,
            "result_groups": result_groups,
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
            "CATALOGUE_BUCKETS": CATALOGUE_BUCKETS,
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
    data.setdefault("group", "tna")
    form = CatalogueSearchForm(data)

    if form.is_valid():
        q = form.cleaned_data.get("q")
        filter_keyword = form.cleaned_data.get("filter_keyword")
        opening_start_date = form.cleaned_data.get("opening_start_date")
        opening_end_date = form.cleaned_data.get("opening_end_date")
        sort_by = form.cleaned_data.get("sort_by")

        response = Record.api.client.search(
            template=Template.DETAILS,
            q=q,
            filter_keyword=filter_keyword,
            filter_aggregations=get_api_filters_from_form_values(form),
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
            opening_start_date=opening_start_date,
            opening_end_date=opening_end_date,
            sort_by=sort_by,
            sort_order=SortOrder.ASC,
        )
        bucket_count_response, result_response = response["responses"]
        update_field_choices_to_refelect_api_response(
            form, result_response["aggregations"]
        )
        records = result_response["hits"]["hits"]
        count = result_response["hits"]["total"]["value"]

    paginator = APIPaginator(count, per_page=per_page)
    page = Page(records, number=page_number, paginator=paginator)
    page_range = paginator.get_elided_page_range(number=page_number, on_ends=0)
    group = data.get("group", "tna")
    try:
        current_bucket = CATALOGUE_BUCKETS.get_bucket(group)
    except KeyError:
        raise Http404(f"Invalid 'group' param value specified: '{group}'")
    return render(
        request,
        "search/catalogue_search.html",
        {
            "page": page,
            "page_range": page_range,
            "form": form,
            "bucket_count_response": bucket_count_response,
            "current_bucket": current_bucket,
            "buckets": CATALOGUE_BUCKETS,
        },
    )


def catalogue_search_long_filter_chooser(request, field_name: str):
    """Output a full(er) list of filter options for a user to choose from.

    Linked to from the catalogue search page and perform the user's current search
    in order to get a suitable list of options to select from.
    """

    # Number of aggregation options to request from the API.
    # (100 is the maximum supported by the API)
    AGGREGATION_SIZE = 100

    data = request.GET.copy()
    data.setdefault("group", "tna")
    form = CatalogueSearchForm(data)
    api_aggregation_name = underscore_to_camelcase(field_name)

    try:
        bound_field = form[field_name]
        field = form.fields[field_name]
    except KeyError:
        raise Http404(
            f"'{field_name}' is not a valid field name. The value must be "
            f"one of: {tuple(form.fields.keys())}."
        )

    if form.is_valid():
        q = form.cleaned_data.get("q")
        filter_keyword = form.cleaned_data.get("filter_keyword")
        opening_start_date = form.cleaned_data.get("opening_start_date")
        opening_end_date = form.cleaned_data.get("opening_end_date")
        sort_by = form.cleaned_data.get("sort_by")
        response = Record.api.client.search(
            q=q,
            filter_keyword=filter_keyword,
            filter_aggregations=get_api_filters_from_form_values(form),
            stream=Stream.EVIDENTIAL,
            aggregations=[
                f"{api_aggregation_name}:{AGGREGATION_SIZE}",
            ],
            opening_start_date=opening_start_date,
            opening_end_date=opening_end_date,
            sort_by=sort_by,
            sort_order=SortOrder.ASC,
            template=Template.DETAILS,
        )
        bucket_count_response, result_response = response["responses"]
        update_field_choices_to_refelect_api_response(
            form, result_response["aggregations"]
        )

    return render(
        request,
        "search/catalogue_search_long_filter_chooser.html",
        {
            "form": form,
            "field_name": field_name,
            "bound_field": bound_field,
            "field": field,
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
    data.setdefault("group", "blog")

    form = WebsiteSearchForm(data)
    if form.is_valid():
        q = form.cleaned_data.get("q")
        filter_keyword = form.cleaned_data.get("filter_keyword")
        opening_start_date = form.cleaned_data.get("opening_start_date")
        opening_end_date = form.cleaned_data.get("opening_end_date")
        sort_by = form.cleaned_data.get("sort_by")

        response = Record.api.client.search(
            template=Template.DETAILS,
            q=q,
            filter_keyword=filter_keyword,
            filter_aggregations=get_api_filters_from_form_values(form),
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
            opening_start_date=opening_start_date,
            opening_end_date=opening_end_date,
            sort_by=sort_by,
            sort_order=SortOrder.ASC,
        )
        bucket_count_response, result_response = response["responses"]
        update_field_choices_to_refelect_api_response(
            form, result_response["aggregations"]
        )
        records = result_response["hits"]["hits"]
        count = result_response["hits"]["total"]["value"]

    paginator = APIPaginator(count, per_page=per_page)
    page = Page(records, number=page_number, paginator=paginator)
    page_range = paginator.get_elided_page_range(number=page_number, on_ends=0)
    try:
        group = data["group"]
    except KeyError:
        raise Http404("No 'group' param value specified.")
    try:
        current_bucket = WEBSITE_BUCKETS.get_bucket(group)
    except KeyError:
        raise Http404(f"Invalid 'group' param value specified: '{group}'")
    return render(
        request,
        "search/website_search.html",
        {
            "page": page,
            "page_range": page_range,
            "form": form,
            "bucket_count_response": bucket_count_response,
            "current_bucket": current_bucket,
            "buckets": WEBSITE_BUCKETS,
        },
    )
