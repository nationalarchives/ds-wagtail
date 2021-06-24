import json
from pathlib import Path

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
