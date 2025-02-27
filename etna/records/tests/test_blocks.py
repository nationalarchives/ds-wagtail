import json
from datetime import datetime, timezone

import responses
from django.conf import settings
from django.urls import reverse
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import nested_form_data, rich_text, streamfield

from etna.articles.models import ArticleIndexPage, ArticlePage
from etna.ciim.tests.factories import create_record, create_response
from etna.images.models import CustomImage

TEST_RECORD_DATA = {
    "iaid": "C123456",
    "reference_number": "ZZ/TEST/1",
    "summary_title": "Test record",
}

BLOCK_TITLE_OVERRIDE = "This record is sooooo featured!"

DATE_1 = datetime(2000, 1, 1, tzinfo=timezone.utc)


class TestFeaturedRecordBlockIntegration(WagtailPageTestCase):
    def setUp(self):
        super().setUp()
        self.login()

        record_response = create_response(records=[create_record(**TEST_RECORD_DATA)])

        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json=record_response,
        )
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetchAll",
            json=record_response,
        )

        root = Site.objects.get().root_page

        self.article_index_page = ArticleIndexPage(
            title="Article Index Page", intro="test", teaser_text="test"
        )
        root.add_child(instance=self.article_index_page)

        self.article_page = ArticlePage(
            title="Article page",
            intro="test",
            teaser_text="test",
        )
        self.article_index_page.add_child(instance=self.article_page)

    @responses.activate
    def test_add_record_links(self):
        test_image = CustomImage.objects.create(width=0, height=0)
        data = nested_form_data(
            {
                "title": "Article page changed",
                "slug": "stories-page",
                "intro": rich_text("test"),
                "hero_image": test_image.id,
                "teaser_text": "test",
                "published_date": DATE_1,
                "body": streamfield(
                    [
                        (
                            "content_section",
                            {
                                "heading": "Heading",
                                "content": streamfield(
                                    [
                                        (
                                            "record_links",
                                            {
                                                "items": streamfield(
                                                    [
                                                        (
                                                            "record_link",
                                                            {
                                                                "record": TEST_RECORD_DATA[
                                                                    "iaid"
                                                                ],
                                                                "descriptive_title": BLOCK_TITLE_OVERRIDE,
                                                                "record_dates": "2020-01-01",
                                                            },
                                                        )
                                                    ]
                                                )
                                            },
                                        )
                                    ]
                                ),
                            },
                        ),
                    ]
                ),
                "page_time_periods-TOTAL_FORMS": 0,
                "page_time_periods-INITIAL_FORMS": 0,
                "page_topics-TOTAL_FORMS": 0,
                "page_topics-INITIAL_FORMS": 0,
                "action-publish": "Publish",
            }
        )

        response = self.client.post(
            reverse("wagtailadmin_pages:edit", args=(self.article_page.id,)),
            data,
        )
        self.assertEqual(len(responses.calls), 2)
        self.assertRedirects(
            response,
            reverse("wagtailadmin_explore", args=(self.article_index_page.id,)),
        )

        self.article_page.refresh_from_db()

        record_links = self.article_page.body[0].value["content"][0]
        record_link = record_links.value["items"][0]

        self.assertEqual(record_links.block_type, "record_links")
        self.assertEqual(record_link["descriptive_title"], BLOCK_TITLE_OVERRIDE)
        self.assertEqual(record_link["record"].iaid, TEST_RECORD_DATA["iaid"])

        self.assertEqual(len(responses.calls), 3)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetch?metadataId=C123456",
        )
        self.assertEqual(
            responses.calls[1].request.url,
            f"{settings.CLIENT_BASE_URL}/fetch?metadataId=C123456",
        )
        self.assertEqual(
            responses.calls[2].request.url,
            f"{settings.CLIENT_BASE_URL}/fetchAll?metadataIds=C123456",
        )

    @responses.activate
    def test_page_with_record_links(self):
        self.article_page.body = json.dumps(
            [
                {
                    "type": "content_section",
                    "value": {
                        "heading": "Heading",
                        "content": [
                            {
                                "type": "record_links",
                                "value": {
                                    "items": [
                                        {
                                            "record": TEST_RECORD_DATA["iaid"],
                                            "descriptive_title": BLOCK_TITLE_OVERRIDE,
                                            "record_dates": "2020-01-01",
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                }
            ]
        )
        self.article_page.save()

        # Wagtail's reference index population will cause the body to be evaluated
        self.assertEqual(len(responses.calls), 0)

        # Check the edit view first
        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=(self.article_page.id,))
        )
        self.assertContains(response, BLOCK_TITLE_OVERRIDE)

        # The record details are requested again to display for the field value
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetchAll?metadataIds=C123456",
        )

        # View the page to check rendering also
        response = self.client.get(self.article_page.get_url())
        self.assertContains(response, BLOCK_TITLE_OVERRIDE)
        self.assertContains(
            response,
            'href="/catalogue/id/' + TEST_RECORD_DATA["iaid"] + '/"',
        )
        self.assertEqual(len(responses.calls), 3)
        self.assertEqual(
            responses.calls[1].request.url,
            f"{settings.CLIENT_BASE_URL}/fetchAll?metadataIds=C123456",
        )

    @responses.activate
    def test_view_edit_page_with_client_api_exception(self):
        """Ensure that even if a record associated with this page doesn't
        exist, we're still able to render its edit page."""

        responses.replace(
            responses.GET, f"{settings.CLIENT_BASE_URL}/fetch", status=500
        )

        self.article_page.body = json.dumps(
            [
                {
                    "type": "content_section",
                    "value": {
                        "heading": "Heading",
                        "content": [
                            {
                                "type": "record_links",
                                "value": {
                                    "items": [
                                        {
                                            "record": TEST_RECORD_DATA["iaid"],
                                            "descriptive_title": BLOCK_TITLE_OVERRIDE,
                                            "record_dates": "2020-01-01",
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                }
            ]
        )
        self.article_page.save()

        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=(self.article_page.id,))
        )

        self.assertEqual(response.status_code, 200)
