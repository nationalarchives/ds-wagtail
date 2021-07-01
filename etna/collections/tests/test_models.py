from django.test import TestCase

from wagtail.core.models import Site, PageViewRestriction

from ..models import TopicExplorerPage, TimePeriodExplorerPage, ExplorerIndexPage


class TestTopicExplorerPages(TestCase):
    def setUp(self):
        root_page = Site.objects.get().root_page

        self.explorer_page = ExplorerIndexPage(
            title="Explorer Page", introduction="Introduction"
        )
        root_page.add_child(instance=self.explorer_page)

    def test_no_child_pages(self):
        self.assertEquals(self.explorer_page.topic_pages.count(), 0)

    def test_unpublish_page_excluded(self):
        unpublished_topic_page = TopicExplorerPage(
            title="Unpublished Topic Page", introduction="Introduction"
        )
        self.explorer_page.add_child(instance=unpublished_topic_page)
        unpublished_topic_page.unpublish()

        self.assertEquals(self.explorer_page.topic_pages.count(), 0)

    def test_private_page_excluded(self):
        private_topic_page = TopicExplorerPage(
            title="Private Topic Page", introduction="Introduction"
        )
        self.explorer_page.add_child(instance=private_topic_page)
        PageViewRestriction.objects.create(page=private_topic_page)

        self.assertEquals(self.explorer_page.topic_pages.count(), 0)

    def test_published_public_pages(self):
        topic_page = TopicExplorerPage(title="Topic Page", introduction="Introduction")
        self.explorer_page.add_child(instance=topic_page)

        self.assertEquals(self.explorer_page.topic_pages.count(), 1)

    def test_published_time_period_pages_excluded(self):
        topic_page = TimePeriodExplorerPage(
            title="Time Period Page",
            introduction="Introduction",
            start_year=1900,
            end_year=1950,
        )
        self.explorer_page.add_child(instance=topic_page)

        self.assertEquals(self.explorer_page.topic_pages.count(), 0)


class TestTimePeriodExplorerPages(TestCase):
    def setUp(self):
        root_page = Site.objects.get().root_page

        self.explorer_page = ExplorerIndexPage(
            title="Explorer Page", introduction="Introduction"
        )
        root_page.add_child(instance=self.explorer_page)

    def test_no_child_pages(self):
        self.assertEquals(self.explorer_page.time_period_pages.count(), 0)

    def test_unpublish_page_excluded(self):
        unpublished_topic_page = TimePeriodExplorerPage(
            title="Unpublished Time Period Page",
            introduction="Introduction",
            start_year=1900,
            end_year=1950,
        )
        self.explorer_page.add_child(instance=unpublished_topic_page)
        unpublished_topic_page.unpublish()

        self.assertEquals(self.explorer_page.time_period_pages.count(), 0)

    def test_private_page_excluded(self):
        private_topic_page = TimePeriodExplorerPage(
            title="Private Time Period Page",
            introduction="Introduction",
            start_year=1900,
            end_year=1950,
        )
        self.explorer_page.add_child(instance=private_topic_page)
        PageViewRestriction.objects.create(page=private_topic_page)

        self.assertEquals(self.explorer_page.time_period_pages.count(), 0)

    def test_published_public_pages(self):
        topic_page = TimePeriodExplorerPage(
            title="Time Period Page",
            introduction="Introduction",
            start_year=1900,
            end_year=1950,
        )
        self.explorer_page.add_child(instance=topic_page)

        self.assertEquals(self.explorer_page.time_period_pages.count(), 1)

    def test_topic_pages_excluded(self):
        topic_page = TopicExplorerPage(title="Topic Page", introduction="Introduction")
        self.explorer_page.add_child(instance=topic_page)

        self.assertEquals(self.explorer_page.time_period_pages.count(), 0)
