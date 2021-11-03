from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse
import csv
import json

import requests

from wagtail.core.models import Page
from wagtail.images import get_image_model

from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import (
    TopicExplorerIndexPage,
    TopicExplorerPage,
    ResultsPage,
    ResultsPageRecordPage,
)

Image = get_image_model()


def get_row(file_name):
    with open(
        file_name,
        newline="",
        encoding="ISO-8859-1",
    ) as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')

        for topic, result_page_name, iaid, description, image_url in reader:

            row = {
                "topic": topic,
                "result_page_name": result_page_name,
                "iaid": iaid,
                "description": description,
                "image_url": image_url,
            }

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

        topic_explorer_index_page = TopicExplorerIndexPage.objects.get()

        result_page_iaids = defaultdict(list)

        for row in get_row(path_to_csv):

            try:
                topic_page = TopicExplorerPage.objects.get(title=row["topic"])
            except TopicExplorerPage.DoesNotExist:
                topic_page = TopicExplorerPage(
                    title=row["topic"],
                    sub_heading="Sub Heading Created During Import.",
                )

            if not topic_page.body.stream_data:
                topic_page.body = json.dumps(
                    [
                        {
                            "type": "collection_highlights",
                            "value": {"heading": "Collection Highlights"},
                        }
                    ]
                )

            if not topic_page.id:
                topic_explorer_index_page.add_child(instance=topic_page)
            else:
                topic_page.save()

            try:
                results_page = (
                    topic_page.get_children()
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
                topic_page.add_child(instance=results_page)
            else:
                results_page.save()

            results_page_record.save()

        # Check that no records have been removed from results
        for title, iaids in result_page_iaids.items():
            results_page = ResultsPage(title=title)
            if results_page.records.exclude(record_iaid__in=iaids).exists():
                print("Warning records have been removed.")
