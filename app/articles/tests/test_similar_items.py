from django.test import TestCase
from django.utils import timezone
from wagtail.models import Site

from ..factories import ArticlePageFactory, FocusedArticlePageFactory
from ..models import ArticlePage, ArticleTag, FocusedArticlePage, TaggedArticle


def _assign_cached_tags(page, slugs, tags_by_slug):
    page.tagged_items = [
        TaggedArticle(tag=tags_by_slug[slug]) for slug in slugs if slug in tags_by_slug
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

    @classmethod
    def setUpTestData(cls):
        root = Site.objects.get(is_default_site=True).root_page

        cls.tags_by_slug = {
            tag.slug: tag
            for tag in ArticleTag.objects.filter(
                slug__in=["americas", "army", "asia", "ufos", "witchcraft"]
            )
        }

        cls.original_page = cls.page_factory(title="Original", parent=root)
        cls.untagged_page = cls.page_factory(title="Untagged", parent=root)
        cls.three_matches_page = cls.page_factory(title="Three", parent=root)
        cls.two_matches_page = cls.page_factory(title="Two", parent=root)
        cls.single_match_page = cls.page_factory(title="Single", parent=root)
        cls.draft_page = cls.page_factory(title="Draft", parent=root, live=False)
        cls.different_tags_page = cls.page_factory(title="Different", parent=root)

        for page in (cls.original_page, cls.three_matches_page, cls.draft_page):
            _assign_cached_tags(page, ["americas", "army", "asia"], cls.tags_by_slug)

        _assign_cached_tags(
            cls.two_matches_page, ["americas", "army"], cls.tags_by_slug
        )
        _assign_cached_tags(cls.single_match_page, ["americas"], cls.tags_by_slug)
        _assign_cached_tags(
            cls.different_tags_page,
            ["ufos", "witchcraft"],
            cls.tags_by_slug,
        )

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

    def test_similar_items_with_tied_publish_dates_returns_expected_set(self):
        tied_time = timezone.now()
        self.page_model.objects.filter(
            id__in=[
                self.three_matches_page.id,
                self.two_matches_page.id,
                self.single_match_page.id,
            ]
        ).update(first_published_at=tied_time)

        test_page = self.page_model.objects.get(id=self.original_page.id)
        related_ids = [page.id for page in test_page.similar_items]

        self.assertEqual(len(related_ids), 3)
        self.assertEqual(len(related_ids), len(set(related_ids)))
        self.assertSetEqual(
            set(related_ids),
            {
                self.three_matches_page.id,
                self.two_matches_page.id,
                self.single_match_page.id,
            },
        )

    def test_similar_items_does_not_duplicate_results_with_duplicate_source_tags(self):
        americas = self.tags_by_slug["americas"]
        army = self.tags_by_slug["army"]
        self.original_page.tagged_items = [
            TaggedArticle(tag=americas),
            TaggedArticle(tag=americas),
            TaggedArticle(tag=army),
        ]
        self.original_page.save()

        test_page = self.page_model.objects.get(id=self.original_page.id)
        related_ids = [page.id for page in test_page.similar_items]

        self.assertEqual(len(related_ids), len(set(related_ids)))


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
