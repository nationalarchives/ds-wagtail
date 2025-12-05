from django.test import TestCase
from wagtail.models import Site

from ..models import ArticlePage, ArticleTag, FocusedArticlePage, TaggedArticle


class TestArticlePageSimilarItems(TestCase):
    def setUp(self):
        root = Site.objects.get().root_page

        # Add pages
        self.original_page = ArticlePage(
            title="Original", intro="test", teaser_text="test"
        )
        root.add_child(instance=self.original_page)

        self.untagged_page = ArticlePage(
            title="Untagged", intro="test", teaser_text="test"
        )
        root.add_child(instance=self.untagged_page)

        self.three_matches_page = ArticlePage(
            title="Three", intro="test", teaser_text="test"
        )
        root.add_child(instance=self.three_matches_page)

        self.two_matches_page = ArticlePage(
            title="Two", intro="test", teaser_text="test"
        )
        root.add_child(instance=self.two_matches_page)

        self.single_match_page = ArticlePage(
            title="Single", intro="test", teaser_text="test"
        )
        root.add_child(instance=self.single_match_page)

        self.draft_page = ArticlePage(
            title="Draft", intro="test", teaser_text="test", live=False
        )
        root.add_child(instance=self.draft_page)
        self.different_tags_page = ArticlePage(
            title="Different", intro="test", teaser_text="test"
        )
        root.add_child(instance=self.different_tags_page)

        # Set tag values for above pages
        for page in (
            self.original_page,
            self.three_matches_page,
            self.draft_page,
        ):
            page.tagged_items = [
                TaggedArticle(tag=t)
                for t in ArticleTag.objects.filter(
                    slug__in=["americas", "army", "asia"]
                )
            ]
            page.save()

        self.two_matches_page.tagged_items = [
            TaggedArticle(tag=t)
            for t in ArticleTag.objects.filter(slug__in=["americas", "army"])
        ]
        self.two_matches_page.save()

        self.single_match_page.tagged_items = [
            TaggedArticle(tag=t) for t in ArticleTag.objects.filter(slug="americas")
        ]
        self.single_match_page.save()

        self.different_tags_page.tagged_items = [
            TaggedArticle(tag=t)
            for t in ArticleTag.objects.filter(slug__in=["ufos", "witchcraft"])
        ]
        self.different_tags_page.save()

    def test_similar_items_ranking(self):
        # Items should be in 'most recent' order
        # No draft items should be included
        test_page = ArticlePage.objects.get(id=self.original_page.id)
        with self.assertNumQueries(3):
            self.assertEqual(
                list(page.id for page in test_page.similar_items),
                [
                    self.three_matches_page.id,
                    self.two_matches_page.id,
                    self.single_match_page.id,
                ],
            )

    def test_all_queries_prevented_when_article_tag_names_is_blank(self):
        test_page = ArticlePage.objects.get(id=self.original_page.id)
        test_page.article_tag_names = ""
        with self.assertNumQueries(0):
            self.assertFalse(test_page.similar_items)

    def test_further_queries_prevented_when_no_tags_available(self):
        test_page = ArticlePage.objects.get(id=self.untagged_page.id)
        test_page.article_tag_names = "foobar"
        with self.assertNumQueries(1):
            self.assertFalse(test_page.similar_items)

    def test_search_prevented_if_no_tag_matches_identified(self):
        test_page = ArticlePage.objects.get(id=self.different_tags_page.id)
        with self.assertNumQueries(3):
            self.assertFalse(test_page.similar_items)


class TestFocusedArticlePageSimilarItems(TestCase):
    def setUp(self):
        root = Site.objects.get().root_page

        # Add pages
        self.original_page = FocusedArticlePage(
            title="Original", intro="test", teaser_text="test"
        )
        root.add_child(instance=self.original_page)

        self.untagged_page = FocusedArticlePage(
            title="Untagged", intro="test", teaser_text="test"
        )
        root.add_child(instance=self.untagged_page)

        self.three_matches_page = FocusedArticlePage(
            title="Three", intro="test", teaser_text="test"
        )
        root.add_child(instance=self.three_matches_page)

        self.two_matches_page = FocusedArticlePage(
            title="Two", intro="test", teaser_text="test"
        )
        root.add_child(instance=self.two_matches_page)

        self.single_match_page = FocusedArticlePage(
            title="Single", intro="test", teaser_text="test"
        )
        root.add_child(instance=self.single_match_page)

        self.draft_page = FocusedArticlePage(
            title="Draft", intro="test", teaser_text="test", live=False
        )
        root.add_child(instance=self.draft_page)

        self.different_tags_page = FocusedArticlePage(
            title="Different", intro="test", teaser_text="test"
        )
        root.add_child(instance=self.different_tags_page)

        # Set tag values for above pages
        for page in (
            self.original_page,
            self.three_matches_page,
            self.draft_page,
        ):
            page.tagged_items = [
                TaggedArticle(tag=t)
                for t in ArticleTag.objects.filter(
                    slug__in=["americas", "army", "asia"]
                )
            ]
            page.save()

        self.two_matches_page.tagged_items = [
            TaggedArticle(tag=t)
            for t in ArticleTag.objects.filter(slug__in=["americas", "army"])
        ]
        self.two_matches_page.save()

        self.single_match_page.tagged_items = [
            TaggedArticle(tag=t) for t in ArticleTag.objects.filter(slug="americas")
        ]
        self.single_match_page.save()

        self.different_tags_page.tagged_items = [
            TaggedArticle(tag=t)
            for t in ArticleTag.objects.filter(slug__in=["ufos", "witchcraft"])
        ]
        self.different_tags_page.save()

    def test_similar_items_ranking(self):
        # Items should be in 'most recent' order
        # No draft items should be included
        test_page = FocusedArticlePage.objects.get(id=self.original_page.id)
        with self.assertNumQueries(3):
            self.assertEqual(
                list(page.id for page in test_page.similar_items),
                [
                    self.three_matches_page.id,
                    self.two_matches_page.id,
                    self.single_match_page.id,
                ],
            )

    def test_all_queries_prevented_when_article_tag_names_is_blank(self):
        test_page = FocusedArticlePage.objects.get(id=self.original_page.id)
        test_page.article_tag_names = ""
        with self.assertNumQueries(0):
            self.assertFalse(test_page.similar_items)

    def test_further_queries_prevented_when_no_tags_available(self):
        test_page = FocusedArticlePage.objects.get(id=self.untagged_page.id)
        test_page.article_tag_names = "foobar"
        with self.assertNumQueries(1):
            self.assertFalse(test_page.similar_items)

    def test_search_prevented_if_no_tag_matches_identified(self):
        test_page = FocusedArticlePage.objects.get(id=self.different_tags_page.id)
        with self.assertNumQueries(3):
            self.assertFalse(test_page.similar_items)
