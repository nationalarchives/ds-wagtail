import json

from django.test import TestCase, Client
from django.apps import apps

from wagtail.core.models import Site

from ..models import Category, CATEGORIES_ICON_PATH
from ...insights.models import InsightsIndexPage, InsightsPage


class CategoriesTestCase(TestCase):
    def setUp(self):
        # Create page structure
        self.root = Site.objects.get().root_page

        self.insights_index_page = InsightsIndexPage(
            title="Insights index page",
            introduction="Here is some intro text.",
        )
        self.root.add_child(instance=self.insights_index_page)

        self.insights_page = InsightsPage(
            title="Insights page",
            introduction="Here is some insightful intro text.",
        )
        self.insights_index_page.add_child(instance=self.insights_page)

    def test_category_icon_discover(self):
        # Create category snippet
        category = Category.objects.create(
            name="Discover our records",
            icon=CATEGORIES_ICON_PATH + "book-open-white.svg",
        )

        # Body field JSON
        body_data = [
            {
                "type": "promoted_item",
                "value": {
                    "title": "test_category_icon_discover",
                    "category": category.id,
                    "publication_date": "2021-07-22",
                    "url": "http://google.co.uk",
                    "cta_label": "CTA label",
                    "teaser_image": None,
                    "teaser_alt_text": "Teaser alt text",
                    "description": "Description text",
                },
            }
        ]

        # Update body field
        self.insights_page.body = json.dumps(body_data)
        self.insights_page.save()

        client = Client()
        response = client.get("/insights-index-page/insights-page/")

        print(response.status_code)
        self.assertEqual(response.status_code, 200)

    def test_category_icon_blog(self):
        # Create category snippet
        category = Category.objects.create(
            name="Blog", icon=CATEGORIES_ICON_PATH + "comment-white.svg"
        )

        # Body field JSON
        body_data = [
            {
                "type": "promoted_item",
                "value": {
                    "title": "test_category_icon_blog",
                    "category": category.id,
                    "publication_date": "2021-07-22",
                    "url": "http://google.co.uk",
                    "cta_label": "CTA label",
                    "teaser_image": None,
                    "teaser_alt_text": "Teaser alt text",
                    "description": "Description text",
                },
            }
        ]

        # Update body field
        self.insights_page.body = json.dumps(body_data)
        self.insights_page.save()

        client = Client()
        response = client.get("/insights-index-page/insights-page/")

        print(response.status_code)
        self.assertEqual(response.status_code, 200)

    # def test_category_icon_podcast(self):

    # def test_category_icon_research(self):

    # def test_category_icon_video(self):

    def test_category_icon_unknown(self):
        # Create category snippet
        category = Category.objects.create(
            name="Unknown", icon=CATEGORIES_ICON_PATH + "unknown.svg"
        )

        # Body field JSON
        body_data = [
            {
                "type": "promoted_item",
                "value": {
                    "title": "test_category_icon_unknown",
                    "category": category.id,
                    "publication_date": "2021-07-22",
                    "url": "http://google.co.uk",
                    "cta_label": "CTA label",
                    "teaser_image": None,
                    "teaser_alt_text": "Teaser alt text",
                    "description": "Description text",
                },
            }
        ]

        # Update body field
        self.insights_page.body = json.dumps(body_data)
        self.insights_page.save()

        client = Client()
        response = client.get("/insights-index-page/insights-page/")

        print(response)
        self.assertEqual(response.status_code, 200)
