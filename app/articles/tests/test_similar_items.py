from django.test import TestCase
from wagtail.models import Site

from ..factories import ArticlePageFactory, FocusedArticlePageFactory
from ..models import ArticlePage, ArticleTag, FocusedArticlePage, TaggedArticle


def _assign_tags(page, slugs):
    page.tagged_items = [
        TaggedArticle(tag=t) for t in ArticleTag.objects.filter(slug__in=slugs)
    ]
    page.save()


class SimilarItemsTestBase:
    """
    Shared setup and common tests for similar-items behaviour.

    Mixed into concrete TestCase subclasses (not a TestCase itself, so pytest
    does not collect it directly). Subclasses must set `page_factory` and
    `page_model`. Any test whose query count differs between page types must be
    overridden in the subclass.
    """

    page_factory = None
    page_model = None

    def setUp(self):
        root = Site.objects.get(is_default_site=True).root_page

        self.original_page = self.page_factory(title="Original", parent=root)
        self.untagged_page = self.page_factory(title="Untagged", parent=root)
        self.three_matches_page = self.page_factory(title="Three", parent=root)
        self.two_matches_page = self.page_factory(title="Two", parent=root)
        self.single_match_page = self.page_factory(title="Single", parent=root)
        self.draft_page = self.page_factory(title="Draft", parent=root, live=False)
        self.different_tags_page = self.page_factory(title="Different", parent=root)

        for page in (self.original_page, self.three_matches_page, self.draft_page):
            _assign_tags(page, ["americas", "army", "asia"])

        _assign_tags(self.two_matches_page, ["americas", "army"])
        _assign_tags(self.single_match_page, ["americas"])
        _assign_tags(self.different_tags_page, ["ufos", "witchcraft"])

    def test_similar_items_ranking(self):
        # Items are ordered by -first_published_at (newest first).
        # single_match is created last in setUp, so it is the most recent;
        # draft items must be excluded.
        test_page = self.page_model.objects.get(id=self.original_page.id)
        with self.assertNumQueries(3):
            self.assertEqual(
                list(page.id for page in test_page.similar_items),
                [
                    self.single_match_page.id,
                    self.two_matches_page.id,
                    self.three_matches_page.id,
                ],
            )

    def test_all_queries_prevented_when_article_tag_names_is_blank(self):
        test_page = self.page_model.objects.get(id=self.original_page.id)
        test_page.article_tag_names = ""
        with self.assertNumQueries(0):
            self.assertFalse(test_page.similar_items)

    def test_further_queries_prevented_when_no_tags_available(self):
        test_page = self.page_model.objects.get(id=self.untagged_page.id)
        test_page.article_tag_names = "foobar"
        with self.assertNumQueries(1):
            self.assertFalse(test_page.similar_items)


class TestArticlePageSimilarItems(SimilarItemsTestBase, TestCase):
    page_factory = ArticlePageFactory
    page_model = ArticlePage

    def test_search_prevented_if_no_tag_matches_identified(self):
        test_page = self.page_model.objects.get(id=self.different_tags_page.id)
        with self.assertNumQueries(4):
            self.assertFalse(test_page.similar_items)


class TestFocusedArticlePageSimilarItems(SimilarItemsTestBase, TestCase):
    page_factory = FocusedArticlePageFactory
    page_model = FocusedArticlePage

    def test_search_prevented_if_no_tag_matches_identified(self):
        test_page = self.page_model.objects.get(id=self.different_tags_page.id)
        with self.assertNumQueries(3):
            self.assertFalse(test_page.similar_items)
