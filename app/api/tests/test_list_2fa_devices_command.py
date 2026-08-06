from io import StringIO
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase


class List2FADevicesCommandTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user_no_2fa = self.user_model.objects.create_user(
            username="no2fa", email="no2fa@example.com", password="pw"
        )
        self.user_with_2fa = self.user_model.objects.create_user(
            username="with2fa", email="with2fa@example.com", password="pw"
        )

    @patch("app.api.management.commands.list_2fa_devices.django_otp.user_has_device")
    def test_missing_2fa_lists_users_without_devices(self, user_has_device_mock):
        out = StringIO()

        # simulate: first user has no devices, second has devices
        def has_device(u, confirmed=True):
            return u.pk == self.user_with_2fa.pk

        user_has_device_mock.side_effect = has_device

        call_command("list_2fa_devices", "--missing-2fa", stdout=out)

        output = out.getvalue()
        self.assertIn(self.user_no_2fa.email, output)
        self.assertNotIn(self.user_with_2fa.email, output)

    @patch("django_otp.plugins.otp_static.models.StaticDevice.objects.filter")
    @patch("app.api.management.commands.list_2fa_devices.django_otp.user_has_device")
    def test_missing_recovery_codes_lists_users_with_2fa_but_no_static(
        self, user_has_device_mock, static_filter_mock
    ):
        out = StringIO()

        # Both users reported as having 2FA; only one has static devices
        def has_device(u, confirmed=True):
            return True

        user_has_device_mock.side_effect = has_device

        # static filter: return exists True for user_with_2fa, False for user_no_2fa
        def static_filter(user=None):
            mq = MagicMock()
            if user.pk == self.user_with_2fa.pk:
                mq.exists.return_value = True
            else:
                mq.exists.return_value = False
            return mq

        static_filter_mock.side_effect = static_filter

        call_command("list_2fa_devices", "--missing-recovery-codes", stdout=out)

        output = out.getvalue()
        # user_no_2fa should appear because they have 2FA (mocked) but no static
        self.assertIn(self.user_no_2fa.email, output)
        # user_with_2fa should not appear
        self.assertNotIn(self.user_with_2fa.email, output)
