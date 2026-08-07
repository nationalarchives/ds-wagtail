from django.contrib.auth import get_user_model
from django.test import TestCase
from django_otp.plugins.otp_static.models import StaticDevice

from app.core.middleware import create_static_device_with_tokens


class CreateStaticDeviceWithTokensTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="recovery-user",
            email="recovery@example.com",
            password="password123",
        )

    def test_generates_requested_number_of_codes(self):
        device, tokens = create_static_device_with_tokens(self.user, count=8, length=12)

        self.assertIsInstance(device, StaticDevice)
        self.assertEqual(len(tokens), 8)
        self.assertTrue(all(len(token) == 12 for token in tokens))

    def test_regeneration_with_delete_existing_replaces_codes(self):
        _, first_codes = create_static_device_with_tokens(self.user, count=4)

        # regenerate and delete existing to rotate codes
        _, second_codes = create_static_device_with_tokens(
            self.user, count=4, delete_existing=True
        )

        devices = StaticDevice.objects.filter(user=self.user)
        self.assertEqual(devices.count(), 1)

        self.assertNotEqual(set(first_codes), set(second_codes))
