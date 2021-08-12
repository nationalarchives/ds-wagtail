from tempfile import gettempdir
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse
import csv
import json
import re

import requests

from wagtail.core.models import Page
from wagtail.images import get_image_model

Image = get_image_model()

from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import (
    TimePeriodExplorerIndexPage,
    TimePeriodExplorerPage,
    ResultsPage,
    ResultsPageRecordPage,
)


def get_row(file_name):
    with open(
        file_name,
        newline="",
        encoding="ISO-8859-1",
    ) as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')

        for time_period, result_page_name, iaid, description, image_url in reader:

            row = {
                "time_period": time_period,
                "result_page_name": result_page_name,
                "iaid": iaid,
                "description": description,
                "image_url": image_url,
            }

            matches = re.search(
                r"^(?P<time_period_name>(\s|\w)+[^(]) \((?P<start_year>\d+) - (?P<end_year>\d+)\)$",
                time_period,
            ).groupdict()

            row.update(matches)

            yield row


def download_image(url):
    response = requests.get(url, verify=False)

    file_name = Path(urlparse(url).path).name
    with open(f"{settings.MEDIA_ROOT}/{file_name}", "wb") as f:
        f.write(response.content)

        return f.name.replace(f"{settings.MEDIA_ROOT}/", "")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("path_to_csv", help="Path to CSV file")

    def handle(self, *args, path_to_csv=None, **options):

        time_period_explorer_index_page = TimePeriodExplorerIndexPage.objects.get()

        for row in get_row(path_to_csv):
            try:
                time_period_page = TimePeriodExplorerPage.objects.get(
                    title=row["time_period_name"]
                )
            except TimePeriodExplorerPage.DoesNotExist:
                time_period_page = TimePeriodExplorerPage(
                    title=row["time_period_name"],
                    sub_heading="Sub Heading Created During Import.",
                )

            if not time_period_page.body.stream_data:
                time_period_page.body = json.dumps(
                    [
                        {
                            "type": "collection_highlights",
                            "value": {"heading": "Collection Highlights"},
                        }
                    ]
                )
            time_period_page.start_year = row["start_year"]
            time_period_page.end_year = row["end_year"]

            if not time_period_page.id:
                time_period_explorer_index_page.add_child(instance=time_period_page)
            else:
                time_period_page.save()

            try:
                results_page = (
                    time_period_page.get_children()
                    .get(title=row["result_page_name"])
                    .specific
                )
            except Page.DoesNotExist:
                results_page = ResultsPage(
                    title=row["result_page_name"],
                    sub_heading="Sub Heading Created During Import.",
                    introduction="Introduction Created During Import",
                )

            try:
                results_page_record = results_page.records.get(record_iaid=row["iaid"])
            except ResultsPageRecordPage.DoesNotExist:
                results_page_record = results_page.records.create(
                    record_iaid=row["iaid"], page=results_page
                )

            if url := row.get("image_url"):
                image_path = download_image(url)
                image, _ = Image.objects.get_or_create(
                    title=row["iaid"], file=image_path
                )
                results_page_record.teaser_image = image

            results_page_record.description = row["description"]

            if not results_page.id:
                time_period_page.add_child(instance=results_page)
            else:
                results_page.save()

            results_page_record.save()
