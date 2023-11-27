from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import TestCase

from ..models import CATEGORIES_ICON_PATH, Category


class CategoriesTestCase(TestCase):
    """Smoke tests to ensure that the static assets for each
    category type exists on disk and can be found with the static
    templatetag."""

    def test_discover_icon(self):
        category = Category.objects.get(name="Discover our records")

        path = finders.find(category.icon_static_path)

        self.assertEqual(
            path,
            f"{settings.BASE_DIR}/etna/categories/static/images/category-svgs/search-white.svg",
        )

    def test_research_icon(self):
        category = Category.objects.get(name="Research")

        path = finders.find(category.icon_static_path)

        self.assertEqual(
            path,
            f"{settings.BASE_DIR}/etna/categories/static/images/category-svgs/book-open-white.svg",
        )

    def test_podcast_icon(self):
        category = Category.objects.get(name="Podcasts")

        path = finders.find(category.icon_static_path)

        self.assertEqual(
            path,
            f"{settings.BASE_DIR}/etna/categories/static/images/category-svgs/headphones-white.svg",
        )

    def test_video_icon(self):
        category = Category.objects.get(name="Video")

        path = finders.find(category.icon_static_path)

        self.assertEqual(
            path,
            f"{settings.BASE_DIR}/etna/categories/static/images/category-svgs/video-white.svg",
        )

    def test_blog_icon(self):
        category = Category.objects.get(name="Blog")

        path = finders.find(category.icon_static_path)

        self.assertEqual(
            path,
            f"{settings.BASE_DIR}/etna/categories/static/images/category-svgs/comment-white.svg",
        )

    def test_category_icon_unknown(self):
        category = Category.objects.create(
            name="Unknown", icon=f"{CATEGORIES_ICON_PATH}/unknown.svg"
        )

        path = finders.find(category.icon_static_path)

        self.assertEqual(path, None)
