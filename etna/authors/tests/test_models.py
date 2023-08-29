from django.test import TestCase

from wagtail.models import Site

from ...images.models import CustomImage
from ..models import AuthorIndexPage, AuthorPage, AuthorTag
from ...articles.models import FocusedArticlePage


class TestAuthorPages(TestCase):
    def setUp(self):
        root = Site.objects.get().root_page

        self.author_index_page = AuthorIndexPage(title="Authors", teaser_text="Test teaser text")
        root.add_child(instance=self.author_index_page)

        self.image = CustomImage.objects.create(width=0, height=0)

        self.author_page = AuthorPage(title="John Doe", role="Author on Test Site", summary="Test summary", image=self.image, teaser_text="Test teaser text")
        self.author_index_page.add_child(instance=self.author_page)

        self.author_tag = AuthorTag.objects.create(author=self.author_page)

        self.focused_article_page = FocusedArticlePage(title="Test Article", intro="Test intro", teaser_text="Test teaser text", author_tags=[self.author_tag])
        root.add_child(instance=self.focused_article_page)

    def test_author_index_page(self):
        print(self.focused_article_page.author_tags)
        self.assertEqual(self.author_index_page.title, "Authors")
        self.assertEqual(self.author_index_page.get_children().count(), 1)
        self.assertEqual(self.author_index_page.get_children().first().title, "John Doe")