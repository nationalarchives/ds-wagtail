from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class BlockUsageReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.superuser = user_model.objects.create_superuser(
            username="block-report-superuser",
            email="block-report-superuser@example.com",
            password="password123",
        )

    def test_block_usage_report_renders_for_superuser(self):
        self.client.force_login(self.superuser)

        with (
            patch(
                "app.core.admin_views.get_block_type_names",
                return_value=["image", "paragraph"],
            ),
            patch(
                "app.core.admin_views.get_block_usage_with_pages",
                return_value={
                    "GeneralPage.body": {
                        "paragraph": {
                            "count": 3,
                            "pages": [
                                {
                                    "id": 123,
                                    "title": "Getting started",
                                    "page_type": "GeneralPage",
                                    "occurrences": 2,
                                },
                                {
                                    "id": 456,
                                    "title": "Help",
                                    "page_type": "GeneralPage",
                                    "occurrences": 1,
                                },
                            ],
                        },
                        "image": {
                            "count": 1,
                            "pages": [
                                {
                                    "id": 789,
                                    "title": "Gallery",
                                    "page_type": "GeneralPage",
                                    "occurrences": 1,
                                }
                            ],
                        },
                    }
                },
            ),
        ):
            response = self.client.get(reverse("block_usage_report"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Block usage report")
        self.assertContains(response, "GeneralPage.body")
        self.assertContains(response, "paragraph")
        self.assertContains(response, "3")
        self.assertContains(response, "Getting started")
        self.assertContains(response, "Gallery")
        self.assertEqual(response.context["total_blocks"], 4)

    def test_block_usage_report_passes_filter_to_query(self):
        self.client.force_login(self.superuser)

        with (
            patch(
                "app.core.admin_views.get_block_type_names",
                return_value=["image", "paragraph"],
            ),
            patch(
                "app.core.admin_views.get_block_usage_with_pages", return_value={}
            ) as mocked,
        ):
            response = self.client.get(
                reverse("block_usage_report"), {"block": "paragraph"}
            )

        self.assertEqual(response.status_code, 200)
        mocked.assert_called_once_with(specific_block="paragraph")
        self.assertEqual(response.context["selected_block"], "paragraph")
