from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from ..models import ArticleIndexPage, ArticlePage, RecordArticlePage


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

        # self.record_article_page = RecordArticlePage(
        #     title="Record Article Page",
        #     intro="test",
        #     teaser_text="test",
        #     record="C123456",
        #     date_text="Test date",
        #     about="Test about",
        # )
        # self.root_page.add_child(instance=self.record_article_page)

    def test_article_index_page(self):
        self.assertPageIsRenderable(self.article_index_page)

    def test_article_page(self):
        self.assertPageIsRenderable(self.article_page)

    # def test_record_article_page(self):
    #     self.assertPageIsRenderable(self.record_article_page)
