import unittest

from django.test import TestCase, override_settings

from wagtail.models import PageViewRestriction, Site

import responses

from ...ciim.tests.factories import create_record, create_response
from ..models import (
    ResultsPage,
    TimePeriodExplorerIndexPage,
    TimePeriodExplorerPage,
    TopicExplorerIndexPage,
    TopicExplorerPage,
)


class TestTopicExplorerIndexPages(TestCase):
    def setUp(self):
        root_page = Site.objects.get().root_page

        self.topic_explorer_index_page = TopicExplorerIndexPage(
            title="Explorer Page", sub_heading="Introduction"
        )
        root_page.add_child(instance=self.topic_explorer_index_page)

    def test_no_child_pages(self):
        self.assertEquals(
            self.topic_explorer_index_page.topic_explorer_pages.count(), 0
        )

    def test_unpublish_page_excluded(self):
        unpublished_topic_page = TopicExplorerPage(
            title="Unpublished Topic Page", sub_heading="Introduction"
        )
        self.topic_explorer_index_page.add_child(instance=unpublished_topic_page)
        unpublished_topic_page.unpublish()

        self.assertEquals(
            self.topic_explorer_index_page.topic_explorer_pages.count(), 0
        )

    @unittest.skip(
        "Disabled test due to all child pages on home being private during beta."
    )
    def test_private_page_excluded(self):
        private_topic_page = TopicExplorerPage(
            title="Private Topic Page", sub_heading="Introduction"
        )
        self.topic_explorer_index_page.add_child(instance=private_topic_page)
        PageViewRestriction.objects.create(page=private_topic_page)

        self.assertEquals(
            self.topic_explorer_index_page.topic_explorer_pages.count(), 0
        )

    def test_published_public_pages(self):
        topic_page = TopicExplorerPage(title="Topic Page", sub_heading="Introduction")
        self.topic_explorer_index_page.add_child(instance=topic_page)

        self.assertEquals(
            self.topic_explorer_index_page.topic_explorer_pages.count(), 1
        )

    def test_published_time_period_pages_excluded(self):
        topic_page = TimePeriodExplorerPage(
            title="Time Period Page",
            sub_heading="Introduction",
            start_year=1900,
            end_year=1950,
        )
        self.topic_explorer_index_page.add_child(instance=topic_page)

        self.assertEquals(
            self.topic_explorer_index_page.topic_explorer_pages.count(), 0
        )


class TestTimePeriodExplorerIndexPages(TestCase):
    def setUp(self):
        root_page = Site.objects.get().root_page

        self.time_period_explorer_index_page = TimePeriodExplorerIndexPage(
            title="Explorer Page", sub_heading="Introduction"
        )
        root_page.add_child(instance=self.time_period_explorer_index_page)

    def test_no_child_pages(self):
        self.assertEquals(
            self.time_period_explorer_index_page.time_period_explorer_pages.count(), 0
        )

    def test_unpublish_page_excluded(self):
        unpublished_topic_page = TimePeriodExplorerPage(
            title="Unpublished Time Period Page",
            sub_heading="Introduction",
            start_year=1900,
            end_year=1950,
        )
        self.time_period_explorer_index_page.add_child(instance=unpublished_topic_page)
        unpublished_topic_page.unpublish()

        self.assertEquals(
            self.time_period_explorer_index_page.time_period_explorer_pages.count(), 0
        )

    @unittest.skip(
        "Disabled test due to all child pages on home being private during beta."
    )
    def test_private_page_excluded(self):
        private_topic_page = TimePeriodExplorerPage(
            title="Private Time Period Page",
            sub_heading="Introduction",
            start_year=1900,
            end_year=1950,
        )
        self.time_period_explorer_index_page.add_child(instance=private_topic_page)
        PageViewRestriction.objects.create(page=private_topic_page)

        self.assertEquals(
            self.time_period_explorer_index_page.time_period_explorer_pages.count(), 0
        )

    def test_published_public_pages(self):
        topic_page = TimePeriodExplorerPage(
            title="Time Period Page",
            sub_heading="Introduction",
            start_year=1900,
            end_year=1950,
        )
        self.time_period_explorer_index_page.add_child(instance=topic_page)

        self.assertEquals(
            self.time_period_explorer_index_page.time_period_explorer_pages.count(), 1
        )

    def test_topic_pages_excluded(self):
        topic_page = TopicExplorerPage(title="Topic Page", sub_heading="Introduction")
        self.time_period_explorer_index_page.add_child(instance=topic_page)

        self.assertEquals(
            self.time_period_explorer_index_page.time_period_explorer_pages.count(), 0
        )


@override_settings(KONG_CLIENT_BASE_URL="https://kong.test")
class TestRecordDescriptionOverride(TestCase):
    def setUp(self):
        root_page = Site.objects.get().root_page

        self.results_page = ResultsPage(
            title="Results Page", sub_heading="Sub heading", introduction="Introduction"
        )

        root_page.add_child(instance=self.results_page)

        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="C123456", description="This is the description from Kong"
                    )
                ]
            ),
        )

    @responses.activate
    def test_override_description_is_rendered(self):
        self.results_page.records.create(
            record_iaid="C123456", description="This is the overridden description"
        )
        self.results_page.save()

        response = self.client.get("/results-page/")

        self.assertContains(response, "This is the overridden description")


@override_settings(KONG_CLIENT_BASE_URL="https://kong.test")
class TestResultsPageIntegration(TestCase):
    def setUp(self):
        root_page = Site.objects.get().root_page

        self.results_page = ResultsPage(
            title="Results Page", sub_heading="Sub heading", introduction="Introduction"
        )

        root_page.add_child(instance=self.results_page)

    @responses.activate
    def test_failed_result_fetch_due_to_404(self):
        responses.add(responses.GET, "https://kong.test/data/fetch", status=404)

        self.results_page.records.create(record_iaid="C123456")
        self.results_page.save()

        response = self.client.get("/results-page/")

        self.assertEquals(200, response.status_code)

    @responses.activate
    def test_failed_result_fetch_due_to_500(self):
        responses.add(responses.GET, "https://kong.test/data/fetch", status=500)

        self.results_page.records.create(record_iaid="C123456")
        self.results_page.save()

        response = self.client.get("/results-page/")

        self.assertEquals(200, response.status_code)

    @responses.activate
    def test_failed_result_fetch_due_to_empty_result_set(self):
        responses.add(
            responses.GET, "https://kong.test/data/fetch", json=create_response()
        )

        self.results_page.records.create(record_iaid="C123456")
        self.results_page.save()

        response = self.client.get("/results-page/")

        self.assertEquals(200, response.status_code)


@override_settings(KONG_CLIENT_BASE_URL="https://kong.test")
class TestResultsPage(TestCase):
    def setUp(self):
        root_page = Site.objects.get().root_page

        self.results_page = ResultsPage(
            title="Results Page", sub_heading="Sub heading", introduction="Introduction"
        )

        root_page.add_child(instance=self.results_page)

        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="C123456", description="This is the description from Kong"
                    )
                ]
            ),
        )

    @responses.activate
    def test_datalayer_results_page(self):
        self.results_page.records.create(record_iaid="C123456")
        self.results_page.save()

        response = self.client.get("/results-page/")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Explorer", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "results page", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "", "customDimension9": "", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": ""}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)
