import json

from django.test import TestCase, Client
from django.apps import apps
from django.templatetags.static import static
from django.contrib.staticfiles import finders


from wagtail.core.models import Site

from ..models import Category, CATEGORIES_ICON_PATH


class CategoriesTestCase(TestCase):
    """Smoke tests to ensure that the static assets for each
    category type exists on disk and can be found with the static
    templatetag."""

    def test_discover_icon(self):
        category = Category.objects.create(
            name="Discover our records",
            icon=CATEGORIES_ICON_PATH + "search-white.svg",
        )

        path = finders.find(category.icon_static_path())

        self.assertEqual(
            path, "/app/etna/categories/static/images/category-svgs/search-white.svg"
        )

    def test_research_icon(self):
        category = Category.objects.create(
            name="Discover our records",
            icon=CATEGORIES_ICON_PATH + "book-open-white.svg",
        )

        path = finders.find(category.icon_static_path())

        self.assertEqual(
            path, "/app/etna/categories/static/images/category-svgs/book-open-white.svg"
        )

    def test_podcast_icon(self):
        category = Category.objects.create(
            name="Blog",
            icon=CATEGORIES_ICON_PATH + "headphones-white.svg",
        )

        path = finders.find(category.icon_static_path())

        self.assertEqual(
            path, "/app/etna/categories/static/images/category-svgs/headphones-white.svg"
        )

    def test_video_icon(self):
        category = Category.objects.create(
            name="Video",
            icon=CATEGORIES_ICON_PATH + "video-white.svg",
        )

        path = finders.find(category.icon_static_path())

        self.assertEqual(
            path, "/app/etna/categories/static/images/category-svgs/video-white.svg"
        )

    def test_blog_icon(self):
        category = Category.objects.create(
            name="Blog",
            icon=CATEGORIES_ICON_PATH + "comment-white.svg",
        )

        path = finders.find(category.icon_static_path())

        self.assertEqual(
            path, "/app/etna/categories/static/images/category-svgs/comment-white.svg"
        )

    def test_category_icon_unknown(self):
        category = Category.objects.create(
            name="Unknown",
            icon=CATEGORIES_ICON_PATH + "unknown.svg",
        )

        path = finders.find(category.icon_static_path())

        self.assertEqual(path, None)
