from django.core.paginator import Page
from django.shortcuts import render

from ..ciim.paginator import APIPaginator
from ..records.models import Record
from .forms import SearchForm


def catalogue_search(request):
    form = SearchForm(request.GET)

    per_page = int(request.GET.get("per_page", 20))
    page_number = int(request.GET.get("page", 1))
    offset = (page_number - 1) * per_page

    records = []
    count = 0

    if form.is_valid():
        # If no keyword is provided, pass None to client to fetch all results.
        keyword = form.cleaned_data.get("keyword") or None

        response = Record.api.client.search(
            keyword=keyword,
            offset=offset,
            size=per_page,
        )
        _, result_response = response["responses"]
        records = result_response["hits"]["hits"]
        count = result_response["hits"]["total"]["value"]

    paginator = APIPaginator(count, per_page=per_page)
    page = Page(records, number=page_number, paginator=paginator)

    return render(
        request,
        "search/catalogue_search.html",
        {
            "page": page,
            "form": form,
            "records": records,
        },
    )
