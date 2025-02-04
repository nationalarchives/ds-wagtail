import json

import responses
from django.conf import settings
from wagtail.test.utils import WagtailPageTestCase

from etna.ciim.tests.factories import create_record, create_response
from etna.core.test_utils import prevent_request_warnings


class TestRecordChooseView(WagtailPageTestCase):
    def setUp(self):
        super().setUp()
        self.login()

        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/searchUnified",
            json=create_response(
                records=[
                    create_record(
                        iaid="C10297",
                        summary_title="Law Officers' Department: Registered Files",
                    ),
                ]
            ),
        )

        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="C10297",
                        summary_title="Law Officers' Department: Registered Files",
                    ),
                ]
            ),
        )

    @responses.activate
    def test_get(self):
        response = self.client.get("/admin/record-chooser/")

        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["step"], "choose")

    @responses.activate
    def test_search(self):
        response = self.client.get("/admin/record-chooser/?q=law&result=true")

        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["step"], "choose")
        self.assertIn("Choose a record", content["html"])
        self.assertInHTML(
            (
                '<a class="item-choice" href="/admin/record-chooser/C10297/">'
                "Law Officers&#x27; Department: Registered Files (C10297)"
                "</a>"
            ),
            content["html"],
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertURLEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?stream=evidential&q=law&from=0&size=10",
        )

    @responses.activate
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

    @responses.activate
    @prevent_request_warnings
    def test_select_failed(self):
        responses.reset()
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json=create_response(),
        )

        response = self.client.get("/admin/record-chooser/invalid/")

        self.assertEqual(response.status_code, 404)
