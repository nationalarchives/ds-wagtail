from django.test import TestCase

from wagtail.models import Site

from ..models import InsightsPage, InsightsTag, TaggedInsights


class TestInsightPageSimilarItems(TestCase):
    def setUp(self):
        root = Site.objects.get().root_page

        # Add pages
        self.original_page = InsightsPage(title="Original", sub_heading="Original")
        root.add_child(instance=self.original_page)
        self.untagged_page = InsightsPage(title="Untagged", sub_heading="Untagged")
        root.add_child(instance=self.untagged_page)
        self.single_match_page = InsightsPage(title="Single", sub_heading="Single")
        root.add_child(instance=self.single_match_page)
        self.two_matches_page = InsightsPage(title="Two", sub_heading="Two")
        root.add_child(instance=self.two_matches_page)
        self.three_matches_page = InsightsPage(title="Three", sub_heading="Three")
        root.add_child(instance=self.three_matches_page)
        self.draft_page = InsightsPage(title="Draft", sub_heading="Draft", live=False)
        root.add_child(instance=self.draft_page)
        self.different_tags_page = InsightsPage(
            title="Different", sub_heading="Different"
        )
        root.add_child(instance=self.different_tags_page)

        # Set tag values for above pages
        for page in (
            self.original_page,
            self.three_matches_page,
            self.draft_page,
        ):
            page.tagged_items = [
                TaggedInsights(tag=t)
                for t in InsightsTag.objects.filter(
                    slug__in=["americas", "army", "asia"]
                )
            ]
            page.save()

        self.two_matches_page.tagged_items = [
            TaggedInsights(tag=t)
            for t in InsightsTag.objects.filter(slug__in=["americas", "army"])
        ]
        self.two_matches_page.save()

        self.single_match_page.tagged_items = [
            TaggedInsights(tag=t) for t in InsightsTag.objects.filter(slug="americas")
        ]
        self.single_match_page.save()

        self.different_tags_page.tagged_items = [
            TaggedInsights(tag=t)
            for t in InsightsTag.objects.filter(slug__in=["ufos", "witchcraft"])
        ]
        self.different_tags_page.save()

    def test_similar_items_ranking(self):
        # Items should be in 'best match' order
        # No draft items should be included
        test_page = InsightsPage.objects.get(id=self.original_page.id)
        with self.assertNumQueries(3):
            self.assertEqual(
                list(test_page.similar_items),
                [
                    self.three_matches_page,
                    self.two_matches_page,
                    self.single_match_page,
                ],
            )

    def test_all_queries_prevented_when_insight_tag_names_is_blank(self):
        test_page = InsightsPage.objects.get(id=self.original_page.id)
        test_page.insight_tag_names = ""
        with self.assertNumQueries(0):
            self.assertFalse(test_page.similar_items)

    def test_further_queries_prevented_when_no_tags_available(self):
        test_page = InsightsPage.objects.get(id=self.untagged_page.id)
        test_page.insight_tag_names = "foobar"
        with self.assertNumQueries(1):
            self.assertFalse(test_page.similar_items)

    def test_search_prevented_if_no_tag_matches_identified(self):
        test_page = InsightsPage.objects.get(id=self.different_tags_page.id)
        with self.assertNumQueries(2):
            self.assertFalse(test_page.similar_items)
