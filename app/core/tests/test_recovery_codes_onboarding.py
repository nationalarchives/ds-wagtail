from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice


@override_settings(WAGTAIL_2FA_REQUIRED=True)
class RecoveryCodesOnboardingTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_superuser(
            username="onboarding-admin",
            email="onboarding@example.com",
            password="password123",
        )

        self.primary_device = TOTPDevice.objects.create(
            user=self.user,
            name="Primary authenticator",
            confirmed=True,
        )

    def _login_as_verified_user(self):
        self.client.force_login(self.user)
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = self.primary_device.persistent_id
        session.save()

    def test_first_admin_request_generates_codes_and_redirects(self):
        self._login_as_verified_user()

        response = self.client.get(reverse("wagtailadmin_home"))

        self.assertRedirects(
            response, reverse("recovery_codes"), fetch_redirect_response=False
        )

        device = StaticDevice.objects.get(user=self.user)
        tokens = list(device.token_set.values_list("token", flat=True))

        self.assertEqual(len(tokens), 10)
        self.assertTrue(all(len(token) == 10 for token in tokens))

        session = self.client.session
        self.assertEqual(session.get("initial_recovery_codes"), tokens)

    def test_recovery_codes_view_shows_once_and_clears_session(self):
        self._login_as_verified_user()
        self.client.get(reverse("wagtailadmin_home"))

        session = self.client.session
        expected_codes = session.get("initial_recovery_codes")
        self.assertTrue(expected_codes)

        response = self.client.get(reverse("recovery_codes"))
        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Please save these recovery codes now", content)
        self.assertTrue(all(code in content for code in expected_codes))

        session = self.client.session
        self.assertNotIn("initial_recovery_codes", session)

    def test_existing_recovery_device_skips_onboarding(self):
        self._login_as_verified_user()
        device = StaticDevice.objects.create(
            user=self.user,
            name="Recovery codes",
            confirmed=True,
        )
        device.token_set.create(token="ABCDEFGHJK")

        response = self.client.get(reverse("wagtailadmin_home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(StaticDevice.objects.filter(user=self.user).count(), 1)
        self.assertNotIn("initial_recovery_codes", self.client.session)

    def test_recovery_codes_view_without_session_redirects_home(self):
        self._login_as_verified_user()

        response = self.client.get(reverse("recovery_codes"))

        self.assertRedirects(
            response,
            reverse("wagtailadmin_home"),
            fetch_redirect_response=False,
        )
