import re

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from wagtail.models import Site

from app.api.models import APIToken
from app.articles.models import ArticleIndexPage, ArticlePage, FocusedArticlePage
from app.collections.models import ExplorerIndexPage
from app.images.models import CustomImage


class PageListingBatchingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.token = APIToken.objects.create(name="page-batching-test")
        cls.root = Site.objects.get(is_default_site=True).root_page
        cls.pages = []
        for i in range(5):
            cls.pages.append(
                cls.root.add_child(
                    instance=FocusedArticlePage(
                        title=f"Batch focused {i}",
                        intro="<p>Intro</p>",
                        teaser_text="Teaser",
                    )
                )
            )
        cls.article = cls.root.add_child(
            instance=ArticlePage(
                title="Batch article", intro="<p>Intro</p>", teaser_text="Teaser"
            )
        )

    def test_generic_page_listing_batches_specific_pages(self):
        for search in (None, "Batch"):
            with self.subTest(search=search):
                params = {
                    "child_of": self.root.pk,
                    "order": "title",
                    "limit": 4,
                    "include_aliases": "true",
                }
                if search:
                    params["search"] = search
                with CaptureQueriesContext(connection) as queries:
                    response = self.client.get(
                        "/api/v2/pages/",
                        params,
                        HTTP_AUTHORIZATION=f"Token {self.token.key}",
                    )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [item["id"] for item in response.json()["items"]],
                    [self.article.pk, *(page.pk for page in self.pages[:3])],
                )
                specific_queries = [
                    query["sql"]
                    for query in queries
                    if 'FROM "articles_focusedarticlepage"' in query["sql"]
                ]
                self.assertEqual(len(specific_queries), 1)
                match = re.search(r"\bIN \(([\d, ]+)\)", specific_queries[0])
                self.assertIsNotNone(match)
                self.assertEqual(
                    {int(pk.strip()) for pk in match.group(1).split(",")},
                    {page.pk for page in self.pages[:3]},
                )

    def test_concrete_type_listing_preserves_pagination(self):
        response = self.client.get(
            "/api/v2/pages/",
            {
                "type": "articles.FocusedArticlePage",
                "child_of": self.root.pk,
                "order": "title",
                "limit": 2,
                "offset": 1,
            },
            HTTP_AUTHORIZATION=f"Token {self.token.key}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.json()["items"]],
            [page.pk for page in self.pages[1:3]],
        )

    def test_foi_multiple_type_listing_batches_specific_pages(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                "/api/v2/foi/",
                {
                    "type": "articles.ArticlePage,articles.FocusedArticlePage",
                    "child_of": self.root.pk,
                    "order": "title",
                    "limit": 4,
                },
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.json()["items"]],
            [self.article.pk, *(page.pk for page in self.pages[:3])],
        )
        specific_queries = [
            query["sql"]
            for query in queries
            if 'FROM "articles_focusedarticlepage"' in query["sql"]
        ]
        self.assertEqual(len(specific_queries), 1)
        self.assertIn(" IN ", specific_queries[0])

    def test_catalogue_batches_top_pages_and_latest_articles(self):
        image = CustomImage.objects.create(
            title="Placeholder", file="placeholder.jpg", width=1, height=1
        )
        explorer = self.root.add_child(
            instance=ExplorerIndexPage(
                title="Explorer",
                intro="<p>Intro</p>",
                teaser_text="Teaser",
                stories_hero_image=image,
            )
        )
        index = explorer.add_child(
            instance=ArticleIndexPage(
                title="Article index", intro="<p>Intro</p>", teaser_text="Teaser"
            )
        )
        top_pages = []
        latest_articles = []
        for i in range(3):
            for parent, result in ((explorer, top_pages), (index, latest_articles)):
                page = parent.add_child(
                    instance=FocusedArticlePage(
                        title=f"Catalogue {i}",
                        intro="<p>Intro</p>",
                        teaser_text="Teaser",
                    )
                )
                result.append(page.pk)

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                "/api/v2/catalogue/landing/",
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )

        self.assertEqual(response.status_code, 200)
        collection = response.json()["explore_the_collection"]
        self.assertEqual(
            {item["id"] for item in collection["top_pages"]}, {index.pk, *top_pages}
        )
        self.assertEqual(
            {item["id"] for item in collection["latest_articles"]},
            set(latest_articles),
        )
        specific_queries = [
            query["sql"]
            for query in queries
            if 'FROM "articles_focusedarticlepage"' in query["sql"]
        ]
        self.assertEqual(len(specific_queries), 2)
        self.assertTrue(all(" IN " in sql for sql in specific_queries))
