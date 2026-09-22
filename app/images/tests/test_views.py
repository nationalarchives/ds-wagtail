import csv
import io

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from wagtail.models import Site
from wagtail_factories import CollectionFactory, ImageFactory

from app.articles.factories import ArticlePageFactory
from app.images.models import CustomImage


class TestImagesWithNoAltTextReportView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="password"
        )
        cls.root_page = Site.objects.get(is_default_site=True).root_page

    def setUp(self):
        self.client.force_login(self.superuser)

    def _get_query_count(self, num_images):
        CustomImage.objects.all().delete()
        ImageFactory.create_batch(num_images, description="")

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(reverse("images_with_no_alt_text_report"))

        self.assertEqual(response.status_code, 200)
        return len(ctx.captured_queries)

    def test_usage_count_query_count_does_not_scale_with_number_of_images(self):
        # Regression test for N+1 queries: usage_count must be resolved via
        # an annotated subquery, not CustomImage.get_usage() per row, or the
        # number of queries would grow linearly with the number of images.
        small_batch_query_count = self._get_query_count(1)
        large_batch_query_count = self._get_query_count(20)

        self.assertEqual(small_batch_query_count, large_batch_query_count)

    def test_report_returns_200_and_lists_images(self):
        image = ImageFactory(title="No alt text image", description="")

        response = self.client.get(reverse("images_with_no_alt_text_report"))

        self.assertEqual(response.status_code, 200)
        self.assertIn(image, response.context["object_list"])

    def test_collection_filter_only_returns_images_in_selected_collection(self):
        other_collection = CollectionFactory(name="Other collection")
        image_in_default_collection = ImageFactory(description="")
        image_in_other_collection = ImageFactory(
            description="", collection=other_collection
        )

        response = self.client.get(
            reverse("images_with_no_alt_text_report"),
            {"collection": other_collection.pk},
        )

        object_list = list(response.context["object_list"])
        self.assertIn(image_in_other_collection, object_list)
        self.assertNotIn(image_in_default_collection, object_list)
