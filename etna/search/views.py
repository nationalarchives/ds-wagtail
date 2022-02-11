from django.conf import settings
from django.shortcuts import render

from .forms import SearchForm
from ..records.models import Record
from ..ciim.client import KongClient


def search_view(request):
    form = SearchForm(request.GET)

    records = []

    if form.is_valid():
        client = KongClient(
            settings.KONG_CLIENT_BASE_URL,
            api_key=settings.KONG_CLIENT_KEY,
            verify_certificates=settings.KONG_CLIENT_VERIFY_CERTIFICATES,
        )
        search_text = form.cleaned_data["search_text"]
        # records = Record.search.filter(keyword=search_text)
        records = client.search(keyword=search_text, size=10)["hits"]["hits"]

    return render(
        request,
        "search/search.html",
        {
            "form": form,
            "records": records,
        },
    )
