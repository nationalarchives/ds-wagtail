from django.shortcuts import render

from ..records.models import Record
from .forms import SearchForm


def catalogue_search(request):
    form = SearchForm(request.GET)

    records = []
    count = 0

    if form.is_valid():
        # If no keyword is provided, pass None to client to fetch all results.
        keyword = form.cleaned_data.get("keyword") or None

        response = Record.api.client.search(keyword=keyword, size=20,)
        _, result_response = response["responses"]
        records = result_response["hits"]["hits"]
        count = result_response["hits"]["total"]["value"]

    return render(
        request,
        "search/search.html",
        {
            "count": count,
            "form": form,
            "records": records,
        },
    )
