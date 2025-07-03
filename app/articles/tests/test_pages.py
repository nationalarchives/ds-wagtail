from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from ..models import ArticleIndexPage, ArticlePage, FocusedArticlePage


class TestPages(WagtailPageTestCase):
    @classmethod
    def setUpTestData(self):
        self.root_page = Site.objects.get().root_page

        self.article_index_page = ArticleIndexPage(
            title="Article Index Page",
            intro="test",
            teaser_text="test",
        )
        self.root_page.add_child(instance=self.article_index_page)

        self.article_page = ArticlePage(
            title="Article page",
            intro="test",
            teaser_text="test",
        )
        self.article_index_page.add_child(instance=self.article_page)

        self.focused_article_page = FocusedArticlePage(
            title="Focused Article page",
            intro="test",
            teaser_text="test",
        )
        self.article_index_page.add_child(instance=self.focused_article_page)

    def test_article_index_page(self):
        self.assertPageIsRenderable(self.article_index_page)

    def test_article_page(self):
        self.assertPageIsRenderable(self.article_page)

    def test_focused_article_page(self):
        self.assertPageIsRenderable(self.focused_article_page)
