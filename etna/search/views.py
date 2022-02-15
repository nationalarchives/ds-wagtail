from django.core.paginator import Page
from django.shortcuts import render

from ..ciim.paginator import APIPaginator
from ..records.models import Record
from .forms import SearchForm


def search_view(request):
    form = SearchForm(request.GET)

    records = []

    per_page = 20
    page_number = int(request.GET.get("page", 1))
    offset = (page_number - 1) * per_page
    search_text = ''
    count = 0

    if form.is_valid():
        search_text = form.cleaned_data["search_text"]
        count, records = Record.api.search(
            keyword=search_text, offset=offset, size=per_page
        )

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
        },
    )
