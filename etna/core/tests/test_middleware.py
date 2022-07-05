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
        self.assertEquals(
            response.headers["Retry-After"], "Fri, 04 Nov 2011 00:05:23 UTC+04:00"
        )


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    MAINTENANCE_MODE=True,
    MAINTENENCE_MODE_ALLOW_IPS=["123.4.5.6", "123.3.2.1"],
)
class TestMaintenanceModeOverride(TestCase):
    @patch("etna.core.middleware.get_client_ip")
    def test_maintenance_mode_bypassed_when_ip_in_allowed_list(
        self, mock_get_client_ip
    ):
        # set ip value that is in allowed list
        mock_get_client_ip.return_value = "123.4.5.6"
        response = self.client.get("/")

        self.assertEquals(response.status_code, 200)

    @patch("etna.core.middleware.get_client_ip")
    @prevent_request_warnings
    def test_maintenance_mode_enforced_when_ip_not_in_allowed_list(
        self, mock_get_client_ip
    ):
        # set ip value that is not in allowed list
        mock_get_client_ip.return_value = "789.0.1.2"
        response = self.client.get("/")

        self.assertEquals(response.status_code, 503)
