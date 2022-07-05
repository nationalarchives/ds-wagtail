from unittest.mock import patch

from django.test import TestCase, override_settings

from ...ciim.utils import prevent_request_warnings


@override_settings(MAINTENANCE_MODE=True)
class TestMaintenanceMode(TestCase):
    def test_without_maintenance_mode_ends(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 503)
        self.assertNotIn("Retry-After", response.headers)

    @prevent_request_warnings
    @override_settings(MAINTENENCE_MODE_ENDS="2011-11-04T00:05:23+04:00")
    def test_maintenance_mode_ends_with_timezone_info(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 503)
        self.assertEquals(
            response.headers["Retry-After"], "Thu, 03 Nov 2011 20:05:23 GMT"
        )

    @prevent_request_warnings
    @override_settings(MAINTENENCE_MODE_ENDS="2011-11-04T00:05:23")
    def test_maintenance_mode_ends_without_timezone_info(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 503)
        self.assertEquals(
            response.headers["Retry-After"], "Fri, 04 Nov 2011 00:05:23 GMT"
        )

    @override_settings(MAINTENENCE_MODE_ALLOW_IPS=["123.4.5.6"])
    @patch("etna.core.middleware.get_client_ip", return_value="123.4.5.6")
    def test_maintenance_mode_bypassed_when_ip_in_allow_list(self, *args):
        response = self.client.get("/")

        self.assertEquals(response.status_code, 200)

    @prevent_request_warnings
    @override_settings(MAINTENENCE_MODE_ALLOW_IPS=["123.4.5.6"])
    @patch("etna.core.middleware.get_client_ip", return_value="789.0.1.2")
    def test_maintenance_mode_enforced_when_ip_not_in_allowed_list(
        self, mock_get_client_ip
    ):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 503)
