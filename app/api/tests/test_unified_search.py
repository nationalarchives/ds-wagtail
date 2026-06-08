from unittest.mock import patch

from django.test import TestCase
from wagtail.models import Page, Site

from app.api.models import APIToken
from app.search.models import ExternalApplication, ExternalApplicationPage


class UnifiedSearchAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_page = Site.objects.get(is_default_site=True).root_page
        cls.api_token = APIToken.objects.create(name="test-token")

        cls.wagtail_page = Page(title="Your order page", slug="your-order-page")
        cls.root_page.add_child(instance=cls.wagtail_page)
        cls.wagtail_page.save_revision().publish()

        cls.application = ExternalApplication.objects.create(
            title="Request a military service record",
            version="1.0",
            base_url="https://example.com",
            description="Search external records",
            type_label="Beta",
            is_active=True,
        )
        cls.external_page = ExternalApplicationPage.objects.create(
            title="Your order summary",
            description="Track your request",
            short_title="Order summary",
            url_path="/your-order-summary",
            application=cls.application,
        )

    @patch("app.api.urls.unified_search.get_search_backend")
    def test_search_returns_both_wagtail_and_external_results(self, mock_backend):
        class FakeBackend:
            def search(self, search_query, queryset):
                if queryset.model == Page:
                    return queryset.filter(title__icontains=search_query)
                return queryset.filter(title__icontains=search_query)

        mock_backend.return_value = FakeBackend()

        response = self.client.get(
            "/api/v2/search/?search=your+order",
            HTTP_AUTHORIZATION=f"Token {self.api_token.key}",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 2)

        types = [item["type"] for item in payload["results"]]
        self.assertIn("wagtail_page", types)
        self.assertIn("external_application", types)

    def test_search_without_query_returns_empty_results(self):
        response = self.client.get(
            "/api/v2/search/", HTTP_AUTHORIZATION=f"Token {self.api_token.key}"
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload, {"count": 0, "results": []})