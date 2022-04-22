import json

from django.test import override_settings
from django.urls import reverse

from wagtail.core.models import Site
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import nested_form_data, streamfield

import responses

from ...ciim.tests.factories import create_record, create_response
from ...insights.models import InsightsIndexPage, InsightsPage


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
)
class TestFeaturedRecordBlockIntegration(WagtailPageTests):
    def setUp(self):
        super().setUp()

        response = create_response(
            records=[
                create_record(
                    iaid="C123456",
                    title="Test record",
                ),
            ]
        )
        responses.add(responses.GET, "https://kong.test/data/fetch", json=response)
        responses.add(responses.GET, "https://kong.test/data/fetchAll", json=response)

        root = Site.objects.get().root_page

        self.insights_index_page = InsightsIndexPage(
            title="Insights Index Page",
            sub_heading="Introduction",
        )
        root.add_child(instance=self.insights_index_page)

        self.insights_page = InsightsPage(
            title="Insights page",
            sub_heading="Introduction",
        )
        self.insights_index_page.add_child(instance=self.insights_page)

    @responses.activate
    def test_add_featured_record(self):
        data = nested_form_data(
            {
                "title": "Insights page changed",
                "slug": "insights-page",
                "sub_heading": "Introduction",
                "body": streamfield(
                    [
                        (
                            "content_section",
                            {
                                "heading": "Heading",
                                "content": streamfield(
                                    [
                                        (
                                            "featured_record",
                                            {
                                                "title": "This record is sooooo featured!",
                                                "record": "C123456",
                                            },
                                        )
                                    ]
                                ),
                            },
                        ),
                    ]
                ),
                "action-publish": "Publish",
            }
        )

        response = self.client.post(
            reverse("wagtailadmin_pages:edit", args=(self.insights_page.id,)), data
        )
        self.assertRedirects(
            response,
            reverse("wagtailadmin_explore", args=(self.insights_index_page.id,)),
        )

        self.insights_page.refresh_from_db()

        featured_record = self.insights_page.body[0].value["content"][0]
        self.assertEqual(featured_record.block_type, "featured_record")
        self.assertEqual(
            featured_record.value["title"], "This record is sooooo featured!"
        )
        self.assertEqual(featured_record.value["record"].iaid, "C123456")
        self.assertEqual(featured_record.value["image"]["image"], None)

        self.assertEqual(len(responses.calls), 3)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?iaid=C123456",
        )
        self.assertEqual(
            responses.calls[1].request.url,
            "https://kong.test/data/fetch?iaid=C123456",
        )
        self.assertEqual(
            responses.calls[2].request.url,
            "https://kong.test/data/fetchAll?iaids=C123456",
        )

    @responses.activate
    def test_page_with_featured_record(self):
        self.insights_page.body = json.dumps(
            [
                {
                    "type": "content_section",
                    "value": {
                        "heading": "Heading",
                        "content": [
                            {
                                "type": "featured_record",
                                "value": {
                                    "title": "This record is sooooo featured!",
                                    "record": "C123456",
                                },
                            }
                        ],
                    },
                }
            ]
        )
        self.insights_page.save()

        # Check the edit view first
        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=(self.insights_page.id,))
        )
        self.assertContains(response, "This record is sooooo featured!")
        self.assertContains(response, "Test record")
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetchAll?iaids=C123456",
        )

        # View the page to check rendering also
        response = self.client.get(self.insights_page.get_url())
        self.assertContains(response, "Test record")
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(
            responses.calls[1].request.url,
            "https://kong.test/data/fetchAll?iaids=C123456",
        )

    @responses.activate
    def test_view_edit_page_with_kong_exception(self):
        """Ensure that even if a record associated with this page doesn't
        exist, we're still able to render its edit page."""

        responses.replace(responses.GET, "https://kong.test/data/fetch", status=500)

        self.insights_page.body = json.dumps(
            [
                {
                    "type": "content_section",
                    "value": {
                        "heading": "Heading",
                        "content": [
                            {
                                "type": "featured_records",
                                "value": {
                                    "heading": "This is a heading",
                                    "introduction": "This is some text",
                                    "items": [
                                        {
                                            "title": "",
                                            "record": "C123456",
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                }
            ]
        )
        self.insights_page.save()

        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=(self.insights_page.id,))
        )

        self.assertEquals(response.status_code, 200)
