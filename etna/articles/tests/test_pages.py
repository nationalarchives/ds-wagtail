from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from ..models import ArticlePage


class TestPages(WagtailPageTestCase):
    @classmethod
    def setUpTestData(self):
        self.root_page = Site.objects.get().root_page

        self.article_page = ArticlePage(
            title="Article page",
            intro="test",
            teaser_text="test",
        )
        self.root_page.add_child(instance=self.article_page)

    def test_article_page(self):
        self.assertPageIsRenderable(self.article_page)
