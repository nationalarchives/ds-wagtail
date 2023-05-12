import json

from django.urls import reverse

from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import nested_form_data, rich_text, streamfield

import responses

from etna.images.models import CustomImage

from ...articles.models import ArticleIndexPage, ArticlePage
from ...ciim.tests.factories import create_record, create_response


class TestFeaturedRecordBlockIntegration(WagtailPageTestCase):
    def setUp(self):
        super().setUp()
        self.login()

        response = create_response(
            records=[
                create_record(
                    iaid="C123456",
                    summary_title="Test record",
                ),
            ]
        )
        responses.add(responses.GET, "https://kong.test/data/fetch", json=response)
        responses.add(responses.GET, "https://kong.test/data/fetchAll", json=response)

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
    def test_add_featured_record(self):
        test_image = CustomImage.objects.create(width=0, height=0)
        data = nested_form_data(
            {
                "title": "Article page changed",
                "slug": "stories-page",
                "intro": rich_text("test"),
                "hero_image": test_image.id,
                "teaser_text": "test",
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
                "page_time_periods-TOTAL_FORMS": 0,
                "page_time_periods-INITIAL_FORMS": 0,
                "page_topics-TOTAL_FORMS": 0,
                "page_topics-INITIAL_FORMS": 0,
                "action-publish": "Publish",
            }
        )

        response = self.client.post(
            reverse("wagtailadmin_pages:edit", args=(self.article_page.id,)), data
        )
        self.assertEqual(len(responses.calls), 3)
        self.assertRedirects(
            response,
            reverse("wagtailadmin_explore", args=(self.article_index_page.id,)),
        )

        self.article_page.refresh_from_db()

        featured_record = self.article_page.body[0].value["content"][0]
        self.assertEqual(featured_record.block_type, "featured_record")
        self.assertEqual(
            featured_record.value["title"], "This record is sooooo featured!"
        )
        self.assertEqual(featured_record.value["record"].iaid, "C123456")
        self.assertEqual(featured_record.value["image"]["image"], None)

        self.assertEqual(len(responses.calls), 4)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?metadataId=C123456",
        )
        self.assertEqual(
            responses.calls[1].request.url,
            "https://kong.test/data/fetch?metadataId=C123456",
        )
        self.assertEqual(
            responses.calls[2].request.url,
            "https://kong.test/data/fetchAll?metadataIds=C123456",
        )

    @responses.activate
    def test_page_with_featured_record(self):
        self.article_page.body = json.dumps(
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
        self.article_page.save()

        # Wagtail's reference index population will cause the body to be evaluated
        self.assertEqual(len(responses.calls), 1)

        # Check the edit view first
        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=(self.article_page.id,))
        )
        self.assertContains(response, "This record is sooooo featured!")
        self.assertContains(response, "Test record")

        # The record details are requested again to display for the field value
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetchAll?metadataIds=C123456",
        )

        # View the page to check rendering also
        response = self.client.get(self.article_page.get_url())
        self.assertContains(response, "C123456")
        self.assertEqual(len(responses.calls), 3)
        self.assertEqual(
            responses.calls[1].request.url,
            "https://kong.test/data/fetchAll?metadataIds=C123456",
        )

    @responses.activate
    def test_view_edit_page_with_kong_exception(self):
        """Ensure that even if a record associated with this page doesn't
        exist, we're still able to render its edit page."""

        responses.replace(responses.GET, "https://kong.test/data/fetch", status=500)

        self.article_page.body = json.dumps(
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
        self.article_page.save()

        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=(self.article_page.id,))
        )

        self.assertEquals(response.status_code, 200)
