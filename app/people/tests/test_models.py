from django.test import TestCase
from wagtail.models import Site

from app.articles.models import FocusedArticlePage
from app.images.models import CustomImage

from ..models import AuthorTag, PeopleIndexPage, PersonPage


class TestAuthorPages(TestCase):
    def setUp(self):
        root = Site.objects.get().root_page

        self.author_index_page = PeopleIndexPage(
            title="People", teaser_text="Test teaser text"
        )
        root.add_child(instance=self.author_index_page)

        self.image = CustomImage.objects.create(width=0, height=0)

        self.author_page = PersonPage(
            title="John Doe",
            role="Author on Test Site",
            summary="Test summary",
            image=self.image,
            teaser_text="Test teaser text",
            first_name="John",
            last_name="Doe",
        )
        self.author_index_page.add_child(instance=self.author_page)

        self.focused_articles = {}
        self.author_tags = {}
        for i in range(4):
            self.focused_articles[f"focused_article{i}"] = FocusedArticlePage(
                title=f"Test Article{i}",
                intro="Test intro",
                teaser_text="Test teaser text",
            )
            root.add_child(instance=self.focused_articles[f"focused_article{i}"])

            self.author_tags[f"author_tag{i}"] = AuthorTag(
                page=self.focused_articles[f"focused_article{i}"],
                author=self.author_page,
            )
            root.add_child(instance=self.author_tags[f"author_tag{i}"])

    def test_author_index_page(self):
        self.assertEqual(self.author_index_page.title, "People")
        self.assertEqual(self.author_index_page.get_children().count(), 1)
        self.assertEqual(
            self.author_index_page.get_children().first().title, "John Doe"
        )

    def test_author_page(self):
        self.assertEqual(self.author_page.title, "John Doe")
        self.assertEqual(self.author_page.role, "Author on Test Site")
        self.assertEqual(self.author_page.summary, "Test summary")
        self.assertEqual(self.author_page.image, self.image)

    def test_focused_article_author(self):
        for i in self.focused_articles:
            self.assertEqual(
                self.focused_articles[i].author_tags.first().author.title,
                "John Doe",
            )

    def test_authored_focused_articles(self):
        for item in self.author_page.authored_focused_articles.all():
            self.assertEqual(item.title in [f"Test Article{i}" for i in range(4)], True)
