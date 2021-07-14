from django.test import TestCase

from wagtail.core.models import Site, PageViewRestriction

from ..models import (
    TopicExplorerIndexPage,
    TopicExplorerPage,
    TimePeriodExplorerIndexPage,
    TimePeriodExplorerPage,
    ExplorerIndexPage,
    ResultsPage,
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


class TestRecordDescriptionOverride(TestCase):
    def setUp(self):
        self.results_page = ResultsPage()
