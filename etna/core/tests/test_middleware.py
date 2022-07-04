from unittest.mock import patch

from django.test import TestCase, override_settings

from ...ciim.utils import prevent_request_warnings


@override_settings(
    MAINTENANCE_MODE=True,
    MAINTENENCE_MODE_ENDS="2011-11-04T00:05:23+04:00",
)
class TestMaintenanceMode(TestCase):
    @prevent_request_warnings
    def test_503_maintenance_mode_for_home_page(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 503)


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    MAINTENANCE_MODE=True,
    MAINTENENCE_MODE_ALLOW_IPS="123.4.5.6",
)
class TestMaintenanceModeOverrrice(TestCase):
    def _mocked_ip(request):
        return "123.4.5.6"

    @patch("etna.core.middleware.get_client_ip", _mocked_ip)
    def test_503_maintenance_mode_override_for_home_page(self):
        response = self.client.get("/")

        self.assertEquals(response.status_code, 200)
