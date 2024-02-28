from django.test import TestCase

from wagtail.models import Site

from ..models import ArticleIndexPage, ArticlePage, ArticleTag


class TestArticleTagClean(TestCase):
    def test_clean_preserves_existing_skos_ids(self):
        tag = ArticleTag(name="Test", slug="test", skos_id="Preserve_Me")
        tag.clean()
        self.assertEqual(tag.skos_id, "Preserve_Me")

    def test_clean_does_not_generate_skos_id_when_no_name_specified(self):
        tag = ArticleTag(slug="test")
        tag.clean()
        self.assertEqual(tag.skos_id, "")

    def test_clean_generates_skos_id_from_name_with_no_conflicts(self):
        tag = ArticleTag(name="Test", slug="test")
        tag.clean()
        self.assertEqual(tag.skos_id, "Test")

    def test_clean_generates_skos_id_from_name_with_conflicts(self):
        ArticleTag.objects.create(name="Test", slug="test", skos_id="Test")
        ArticleTag.objects.create(name="Test 2", slug="test-2", skos_id="Test_2")

        tag = ArticleTag(name="Test", slug="test-3")
        tag.clean()
        self.assertEqual(tag.skos_id, "Test_3")


class TestArticleIndexPage(TestCase):
    def setUp(self):
        self.root_page = Site.objects.get().root_page

        self.article_index_page = ArticleIndexPage(
            title="Article Index Page",
            intro="test",
            teaser_text="test",
        )
        self.root_page.add_child(instance=self.article_index_page)

        self.article_page1 = ArticlePage(
            title="Article page 1",
            intro="test",
            teaser_text="test",
        )
        self.article_index_page.add_child(instance=self.article_page1)

        self.article_page2 = ArticlePage(
            title="Article page 2",
            intro="test",
            teaser_text="test",
        )
        self.article_index_page.add_child(instance=self.article_page2)

        self.article_page3 = ArticlePage(
            title="Article page 3",
            intro="test",
            teaser_text="test",
        )
        self.article_index_page.add_child(instance=self.article_page3)

    def test_get_article_pages(self):
        context = self.article_index_page.get_context(request=None)
        self.assertEqual(len(context["article_pages"]), 3)

    def test_check_article_pages(self):
        context = self.article_index_page.get_context(request=None)
        children = self.article_index_page.get_children()
        for i, page in enumerate(context["article_pages"]):
            self.assertEqual(page.title, children[i].title)
