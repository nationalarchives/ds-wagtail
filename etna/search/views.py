from django.core.paginator import Page
from django.shortcuts import render

from ..ciim.paginator import APIPaginator
from ..ciim.client import SortOrder
from ..records.models import Record
from .forms import SearchForm


def search_view(request):
    form = SearchForm(request.GET)

    response = {}
    records = []

    per_page = 20
    page_number = int(request.GET.get("page", 1))
    offset = (page_number - 1) * per_page
    search_text = ""
    count = 0

    if form.is_valid():
        search_text = form.cleaned_data["search_text"]
        bucket = form.cleaned_data["bucket"]
        sort = form.cleaned_data["sort"]

        response = Record.api.client.search(
            keyword=search_text,
            offset=offset,
            size=per_page,
            show_buckets=True,
            buckets=[bucket],
            sort_by=sort,
            sort_order=SortOrder.ASC,
        )
        count, records = Record.api.transform(response=response)

    paginator = APIPaginator(count, per_page=per_page)
    page = Page(records, number=page_number, paginator=paginator)

    return render(
        request,
        "search/search.html",
        {
            "search_text": search_text,
            "count": count,
            "form": form,
            "page": page,
            "response": response,
        },
    )
