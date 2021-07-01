from http import HTTPStatus
from pathlib import Path
import json

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse

from wagtail.core.models import Site
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import inline_formset, nested_form_data

from ..models import ExplorerIndexPage, TopicExplorerPage, ResultsPage


@override_settings(
    KONG_CLIENT_TEST_MODE=True,
    KONG_CLIENT_TEST_FILENAME=Path(
        settings.BASE_DIR, "etna", "ciim", "tests/fixtures/record.json"
    ),
)
class TestRecordChooseView(WagtailPageTests):
    def test_get(self):
        response = self.client.get("/admin/record-chooser/")

        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["step"], "choose")

    def test_search(self):
        response = self.client.get("/admin/record-chooser/?q=law&result=true")

        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["step"], "choose")
        self.assertIn("Choose a record", content["html"])
        self.assertInHTML(
            '<a class="item-choice" href="/admin/record-chooser/C10297/">Law Officers&#x27; Department: Registered Files (C10297)</a>',
            content["html"],
        )

    def test_select(self):
        response = self.client.get("/admin/record-chooser/C10297/")

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)

        self.assertEqual(content["step"], "chosen")
        self.assertEqual(
            content["result"],
            {
                "id": "C10297",
                "string": "Law Officers' Department: Registered Files (C10297)",
                "edit_link": None,
            },
        )

    def test_select_failed(self):
        response = self.client.get("/admin/record-chooser/invalid/")

        self.assertEqual(response.status_code, 404)


class TestEditResultsPage(WagtailPageTests):
    def setUp(self):
        super().setUp()

        root = Site.objects.get().root_page

        explorer_page = ExplorerIndexPage(
            title="Explorer Index Page", introduction="Introduction"
        )
        root.add_child(instance=explorer_page)

        self.topic_page = TopicExplorerPage(title="Topic", introduction="Introduction")
        explorer_page.add_child(instance=self.topic_page)

        self.results_page = ResultsPage(title="Results")
        self.topic_page.add_child(instance=self.results_page)

    def test_add_records(self):
        data = nested_form_data(
            {
                "seo_title": "Results",
                "slug": "results",
                "records": inline_formset(
                    [
                        {
                            "id": "",
                            "record_iaid": "C10297",
                        }
                    ],
                ),
                "action-publish": "Publish",
                "search_description": "",
            }
        )

        response = self.client.post(
            reverse("wagtailadmin_pages:edit", args=(self.results_page.id,)), data
        )

        self.assertRedirects(
            response, reverse("wagtailadmin_explore", args=(self.topic_page.id,))
        )
        self.assertEqual(self.results_page.records.count(), 1)

    def test_remove_records(self):
        self.results_page.records.create(record_iaid="C140", page=self.results_page)
        self.results_page.save()

        data = nested_form_data(
            {
                "seo_title": "Results",
                "slug": "results",
                "records": inline_formset(
                    [
                        {
                            "id": "",
                            "record_iaid": "C10297",
                        }
                    ], initial=1
                ),
                "action-publish": "Publish",
                "search_description": "",
            }
        )
        data['records-0-DELETE'] = '1'
        data['records-0-id'] = self.results_page.records.first().id

        response = self.client.post(
            reverse("wagtailadmin_pages:edit", args=(self.results_page.id,)), data
        )

        self.assertRedirects(
            response, reverse("wagtailadmin_explore", args=(self.topic_page.id,))
        )
        self.assertEqual(self.results_page.records.count(), 0)

    def test_view_edit_page(self):
        """Viewing an edit page for a ResultsPage with associated records requires a
        request to Kong to fetch the record details. This test is a smoke test to ensure
        the page can load.
        """
        self.results_page.records.create(record_iaid="C140", page=self.results_page)

        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=(self.results_page.id,))
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
