from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from wagtail.models import Page, Site

from app.articles.models import (
    ArticlePage,
    ArticleTag,
    FocusedArticlePage,
    TaggedArticle,
)
from app.core.serializers.pages import get_api_data


class ArticleTagsAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        root = Site.objects.get(is_default_site=True).root_page
        tag = ArticleTag.objects.create(
            name="Example", slug="example", skos_id="example"
        )
        cls.page_ids = []
        for i in range(5):
            page = root.add_child(
                instance=FocusedArticlePage(
                    title=f"Article {i}", intro="<p>Intro</p>", teaser_text="Teaser"
                )
            )
            page.tagged_items = [TaggedArticle(tag=tag)]
            page.save()
            Page.objects.filter(pk=page.pk).update(
                first_published_at=datetime(2020, 1, 1, tzinfo=UTC) + timedelta(days=i)
            )
            cls.page_ids.insert(0, page.pk)

    def test_limit_is_applied_before_serialization(self):
        for limit, expected_count in [
            (None, 3),
            ("2", 2),
            ("0", 0),
            ("-1", 4),
            ("-8", 0),
            (str(10**30), 5),
        ]:
            with self.subTest(limit=limit):
                params = {"tags": "example"}
                if limit is not None:
                    params["limit"] = limit
                with patch(
                    "app.core.serializers.pages.get_api_data", wraps=get_api_data
                ) as serialize_page:
                    response = self.client.get("/api/v2/article_tags/", params)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [item["id"] for item in response.json()],
                    self.page_ids[:expected_count],
                )
                self.assertEqual(serialize_page.call_count, expected_count)

    def test_specific_pages_are_fetched_in_bulk(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                "/api/v2/article_tags/", {"tags": "example", "limit": 5}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.json()], self.page_ids)
        specific_queries = [
            query["sql"]
            for query in queries
            if 'FROM "articles_focusedarticlepage"' in query["sql"]
        ]
        self.assertEqual(len(specific_queries), 1)
        self.assertIn(" IN ", specific_queries[0])

    def test_specific_pages_preserve_mixed_types_and_order(self):
        root = Site.objects.get(is_default_site=True).root_page
        article = root.add_child(
            instance=ArticlePage(
                title="Other article", intro="<p>Intro</p>", teaser_text="Teaser"
            )
        )
        article.tagged_items = [
            TaggedArticle(tag=ArticleTag.objects.get(slug="example"))
        ]
        article.save()
        Page.objects.filter(pk=article.pk).update(
            first_published_at=datetime(2021, 1, 1, tzinfo=UTC)
        )

        response = self.client.get(
            "/api/v2/article_tags/", {"tags": "example", "limit": 6}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.json()], [article.pk, *self.page_ids]
        )
        self.assertEqual(
            [item["type"] for item in response.json()],
            ["articles.ArticlePage"] + ["articles.FocusedArticlePage"] * 5,
        )
