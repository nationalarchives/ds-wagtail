from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from wagtail.core.models import Group

import responses

from ...ciim.tests.factories import create_record, create_response
from ...ciim.utils import prevent_request_warnings

User = get_user_model()


@override_settings(
    MAINTENANCE_MODE=True,
    MAINTENENCE_MODE_ENDS="2011-11-04T00:05:23+04:00",
)
class TestMaintenanceMode(TestCase):
    @prevent_request_warnings
    def test_503_maintenance_override_for_home_page(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 503)


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    MAINTENANCE_MODE=True,
    MAINTENENCE_MODE_ALLOW_IPS="123.4.5.6",
)
class TestMaintenanceModeOverrrice(TestCase):
    def setUp(self):

        private_beta_user = User(
            username="private-beta@email.com", email="private-beta@email.com"
        )
        private_beta_user.set_password("password")
        private_beta_user.save()
        private_beta_user.groups.add(Group.objects.get(name="Beta Testers"))

        self.client.login(email="private-beta@email.com", password="password")

    def _mocked_ip(request):
        return "123.4.5.6"

    @patch("etna.core.middleware.get_client_ip", _mocked_ip)
    @responses.activate
    def test_503_maintenance_override_for_record_detail(self):

        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456"),
                ]
            ),
        )

        response = self.client.get("/catalogue/C123456/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.resolver_match.view_name, "details-page-machine-readable"
        )
        self.assertTemplateUsed(response, "records/record_page.html")
