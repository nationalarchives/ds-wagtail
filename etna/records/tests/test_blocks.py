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
        responses.add(responses.GET, "https://kong.test/search", json=response)
        responses.add(responses.GET, "https://kong.test/data/fetch", json=response)

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
                "body": streamfield([
                    ("featured_record",
                     {"record": "C123456"}
                     ), ]
                ),
                "action-publish": "Publish",
            }
        )

        response = self.client.post(
            reverse("wagtailadmin_pages:edit", args=(self.insights_page.id,)), data
        )
        self.insights_page.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("wagtailadmin_explore", args=(self.insights_index_page.id,)),
        )

        self.assertEqual(

            self.insights_page.body[0].block_type, "featured_record"
        )
        self.assertEqual(
            self.insights_page.body[0].value["record"].iaid,
            "C123456"
        )
        self.assertEqual(
            self.insights_page.body[0].value["image"]["image"],
            None
        )

        self.assertEqual(len(responses.calls), 3)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?iaid=C123456&from=0&pretty=false&expand=false",
        )
        self.assertEqual(
            responses.calls[1].request.url,
            "https://kong.test/data/fetch?iaid=C123456&from=0&pretty=false&expand=false",
        )

    @responses.activate
    def test_remove_records(self):
        self.insights_page.body = json.dumps(
            [
                {
                    "type": "featured_record",
                    "value": {"record": "C123456"},
                }
            ]
        )
        self.insights_page.save()

        data = nested_form_data(
            {
                "title": "Insights page changed",
                "slug": "insights-page",
                "sub_heading": "Introduction",
                "body": streamfield([]),
                "action-publish": "Publish",
            }
        )

        response = self.client.post(
            reverse("wagtailadmin_pages:edit", args=(self.insights_page.id,)), data
        )
        self.insights_page.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("wagtailadmin_explore", args=(self.insights_index_page.id,)),
        )
        self.assertEqual(len(self.insights_page.body), 0)

        self.assertEqual(len(responses.calls), 0)

    @responses.activate
    def test_validation_error_if_no_record_in_post(self):
        data = nested_form_data(
            {
                "title": "Insights page changed",
                "slug": "insights-page",
                "sub_heading": "Introduction",
                "body": streamfield(
                    [
                        ("featured_record", {"record": ""}),
                    ]
                ),
                "action-publish": "Publish",
            }
        )

        response = self.client.post(
            reverse("wagtailadmin_pages:edit", args=(self.insights_page.id,)), data
        )

        # Finding a block error within the form is tricky. For now let's assume that if
        # an error is raised in the StreamBlock, then the record chooser is responsible.
        self.assertEqual(
            response.context["form"].errors,
            {"body": ["Validation error in StreamBlock"]},
        )

    @responses.activate
    def test_view_edit_page_with_featured_record(self):
        self.insights_page.body = json.dumps(
            [
                {
                    "type": "featured_record",
                    "value": {"record": "C123456"},
                }
            ]
        )
        self.insights_page.save()

        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=(self.insights_page.id,))
        )

        self.assertContains(response, "Test record")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?iaid=C123456&from=0&pretty=false&expand=false",
        )

    @responses.activate
    def test_view_edit_page_with_kong_exception(self):
        """Ensure that even if a record associated with this page doesn't
        exist, we're still able to render its edit page."""

        responses.add(responses.GET, "https://kong.test/data/fetch", status=500)

        self.insights_page.body = json.dumps(
            [
                {
                    "type": "featured_records",
                    "value": {
                        "heading": "This is a heading",
                        "introduction": "This is some text",
                        "records": ["C123456"],
                    },
                }
            ]
        )
        self.insights_page.save()

        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=(self.insights_page.id,))
        )

        self.assertEquals(response.status_code, 200)

    @responses.activate
    def test_view_page_with_featured_record(self):
        self.insights_page.body = json.dumps(
            [
                {
                    "type": "featured_record",
                    "value": {"record": "C123456"},
                }
            ]
        )
        self.insights_page.save()

        response = self.client.get(self.insights_page.get_url())

        self.assertContains(response, "Test record")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?iaid=C123456&from=0&pretty=false&expand=false",
        )


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
)
class TestFeaturedRecordsBlockIntegration(WagtailPageTests):
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
        responses.add(responses.GET, "https://kong.test/search", json=response)
        responses.add(responses.GET, "https://kong.test/data/fetch", json=response)

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
    def test_add_featured_records(self):
        data = nested_form_data(
            {
                "title": "Insights page changed",
                "slug": "insights-page",
                "sub_heading": "Introduction",
                "body": streamfield(
                    [
                        (
                            "featured_records",
                            {
                                "heading": "This is a heading",
                                "introduction": "This is some text",
                                "records": streamfield([("value", "C123456")]),
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
        self.insights_page.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("wagtailadmin_explore", args=(self.insights_index_page.id,)),
        )
        self.assertEqual(
            self.insights_page.body[0].block_type, "featured_records"
        )

        self.assertEqual(
            self.insights_page.body[0].value["heading"],
            "This is a heading"
        )
        self.assertEqual(
            self.insights_page.body[0].value["introduction"],
            "This is some text"
        )
        self.assertEqual(
            self.insights_page.body[0].value["records"][0].iaid,
            "C123456"
        )
        self.assertEqual(len(responses.calls), 3)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?iaid=C123456&from=0&pretty=false&expand=false",
        )
        self.assertEqual(
            responses.calls[1].request.url,
            "https://kong.test/data/fetch?iaid=C123456&from=0&pretty=false&expand=false",
        )

    @responses.activate
    def test_remove_records(self):
        self.insights_page.body = json.dumps(
            [
                {
                    "type": "featured_records",
                    "value": {
                        "heading": "This is a heading",
                        "introduction": "This is some text",
                        "records": ["C123456"],
                    },
                }
            ]
        )
        self.insights_page.save()

        data = nested_form_data(
            {
                "title": "Insights page changed",
                "slug": "insights-page",
                "sub_heading": "Introduction",
                "body": streamfield([]),
                "action-publish": "Publish",
            }
        )

        response = self.client.post(
            reverse("wagtailadmin_pages:edit", args=(self.insights_page.id,)), data
        )
        self.insights_page.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("wagtailadmin_explore", args=(self.insights_index_page.id,)),
        )
        self.assertEqual(len(self.insights_page.body), 0)

        self.assertEqual(len(responses.calls), 0)

    @responses.activate
    def test_view_edit_page_with_featured_record(self):
        self.insights_page.body = json.dumps(
            [
                {
                    "type": "featured_records",
                    "value": {
                        "heading": "This is a heading",
                        "introduction": "This is some text",
                        "records": ["C123456"],
                    },
                }
            ]
        )
        self.insights_page.save()

        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=(self.insights_page.id,))
        )

        self.assertContains(response, "Test record")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?iaid=C123456&from=0&pretty=false&expand=false",
        )

    @responses.activate
    def test_view_edit_page_with_featured_record_not_in_kong(self):
        """Ensure that even if a record associated with this page doesn't
        exist, we're still able to render its edit page."""

        responses.add(
            responses.GET, "https://kong.test/data/fetch", json=create_response()
        )

        self.insights_page.body = json.dumps(
            [
                {
                    "type": "featured_records",
                    "value": {
                        "heading": "This is a heading",
                        "introduction": "This is some text",
                        "records": ["C123456"],
                    },
                }
            ]
        )
        self.insights_page.save()

        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=(self.insights_page.id,))
        )

        self.assertEquals(response.status_code, 200)

    @responses.activate
    def test_view_page_with_featured_record(self):
        self.insights_page.body = json.dumps(
            [
                {
                    "type": "featured_records",
                    "value": {
                        "heading": "This is a heading",
                        "introduction": "This is some text",
                        "records": ["C123456"],
                    },
                }
            ]
        )
        self.insights_page.save()

        response = self.client.get(self.insights_page.get_url())

        self.assertContains(response, "Test record")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?iaid=C123456&from=0&pretty=false&expand=false",
        )
