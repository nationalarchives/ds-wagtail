from django.test import TestCase
from wagtail.models import Site

from ..models import (
    TimePeriodExplorerIndexPage,
    TimePeriodExplorerPage,
    TopicExplorerIndexPage,
    TopicExplorerPage,
)


class TestTopicExplorerIndexPages(TestCase):
    def setUp(self):
        root_page = Site.objects.get(is_default_site=True).root_page

        self.topic_explorer_index_page = TopicExplorerIndexPage(
            title="Explorer Page", intro="test", teaser_text="test"
        )
        root_page.add_child(instance=self.topic_explorer_index_page)

    def test_no_child_pages(self):
        self.assertEqual(self.topic_explorer_index_page.explorer_pages.count(), 0)

    def test_unpublish_page_excluded(self):
        unpublished_topic_page = TopicExplorerPage(
            title="Unpublished Topic Page", intro="test", teaser_text="test"
        )
        self.topic_explorer_index_page.add_child(instance=unpublished_topic_page)
        unpublished_topic_page.unpublish()

        self.assertEqual(self.topic_explorer_index_page.explorer_pages.count(), 0)

    def test_published_public_pages(self):
        topic_page = TopicExplorerPage(
            title="Topic Page", intro="test", teaser_text="test"
        )
        self.topic_explorer_index_page.add_child(instance=topic_page)

        self.assertEqual(self.topic_explorer_index_page.explorer_pages.count(), 1)

    def test_published_time_period_pages_excluded(self):
        topic_page = TimePeriodExplorerPage(
            title="Time Period Page",
            intro="test",
            teaser_text="test",
            start_year=1900,
            end_year=1950,
        )
        self.topic_explorer_index_page.add_child(instance=topic_page)

        self.assertEqual(self.topic_explorer_index_page.explorer_pages.count(), 0)


class TestTopicExplorerPage(TestCase):
    def setUp(self):
        root_page = Site.objects.get(is_default_site=True).root_page
        self.index_page = TopicExplorerIndexPage(
            title="Topics", intro="topics", teaser_text="topics"
        )
        root_page.add_child(instance=self.index_page)
        self.topic_page = TopicExplorerPage(
            title="Test Topic",
            skos_id="Test_Topic",
            slug="topic",
            teaser_text="test",
            intro="test",
        )
        self.index_page.add_child(instance=self.topic_page)

    def test_clean_preserves_existing_skos_ids(self):
        self.topic_page.clean()
        self.assertEqual(self.topic_page.skos_id, "Test_Topic")

        self.topic_page.skos_id = "new-SKOS-id"
        self.topic_page.clean()
        self.assertEqual(self.topic_page.skos_id, "new-SKOS-id")

    def test_clean_does_not_generate_skos_id_when_no_title_specified(self):
        self.topic_page.title = ""
        self.topic_page.skos_id = ""
        self.topic_page.clean()
        self.assertEqual(self.topic_page.skos_id, "")

    def test_clean_generates_skos_id_from_title_with_no_conflicts(self):
        self.topic_page.skos_id = ""
        self.topic_page.clean()
        self.assertEqual(self.topic_page.skos_id, "Test_Topic")

    def test_clean_generates_skos_id_from_title_with_conflicts(self):
        self.index_page.add_child(
            instance=TopicExplorerPage(
                title="Test Topic 2",
                skos_id="Test_Topic_2",
                slug="topic-2",
                teaser_text="test",
                intro="test",
            )
        )
        self.index_page.add_child(
            instance=TopicExplorerPage(
                title="Test Topic 3",
                skos_id="Test_Topic_3",
                slug="topic-3",
                teaser_text="test",
                intro="test",
            )
        )

        obj = TopicExplorerPage(title="Test Topic")
        obj.clean()
        self.assertEqual(obj.skos_id, "Test_Topic_4")

    def test_page_skos_id_preserved_when_revision_value_differs(self):
        self.topic_page.skos_id = "SomeOtherValue"
        revision = self.topic_page.save_revision()
        self.topic_page.refresh_from_db()

        topic_page_recreated = revision.as_object()

        # Thanks to with_content_json() overrides, the recreated topic page
        # should retain the `skos_id` value saved for `self.topic_page`
        # initally, and ignore the new value from the revision
        self.assertEqual(topic_page_recreated.skos_id, "Test_Topic")


class TestTimePeriodExplorerIndexPages(TestCase):
    def setUp(self):
        root_page = Site.objects.get(is_default_site=True).root_page

        self.time_period_explorer_index_page = TimePeriodExplorerIndexPage(
            title="Explorer Page", intro="test", teaser_text="test"
        )
        root_page.add_child(instance=self.time_period_explorer_index_page)

    def test_no_child_pages(self):
        self.assertEqual(self.time_period_explorer_index_page.explorer_pages.count(), 0)

    def test_unpublish_page_excluded(self):
        unpublished_topic_page = TimePeriodExplorerPage(
            title="Unpublished Time Period Page",
            intro="test",
            teaser_text="test",
            start_year=1900,
            end_year=1950,
        )
        self.time_period_explorer_index_page.add_child(instance=unpublished_topic_page)
        unpublished_topic_page.unpublish()

        self.assertEqual(self.time_period_explorer_index_page.explorer_pages.count(), 0)

    def test_published_public_pages(self):
        topic_page = TimePeriodExplorerPage(
            title="Time Period Page",
            intro="test",
            teaser_text="test",
            start_year=1900,
            end_year=1950,
        )
        self.time_period_explorer_index_page.add_child(instance=topic_page)

        self.assertEqual(self.time_period_explorer_index_page.explorer_pages.count(), 1)

    def test_topic_pages_excluded(self):
        topic_page = TopicExplorerPage(
            title="Topic Page", intro="test", teaser_text="test"
        )
        self.time_period_explorer_index_page.add_child(instance=topic_page)

        self.assertEqual(self.time_period_explorer_index_page.explorer_pages.count(), 0)
