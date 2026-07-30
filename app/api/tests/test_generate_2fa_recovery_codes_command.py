from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django_otp.plugins.otp_static.models import StaticDevice


class Generate2FARecoveryCodesCommandTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="recovery-user",
            email="recovery@example.com",
            password="password123",
        )

    def test_target_user_not_found_raises_command_error(self):
        out = StringIO()

        with self.assertRaises(CommandError):
            call_command(
                "generate_2fa_recovery_codes",
                "--target-email",
                "missing@example.com",
                stdout=out,
            )

    def test_generates_requested_number_of_codes_without_printing_them(self):
        out = StringIO()

        call_command(
            "generate_2fa_recovery_codes",
            "--target-email",
            self.user.email,
            "--count",
            "8",
            "--length",
            "12",
            stdout=out,
        )

        device = StaticDevice.objects.get(user=self.user)
        tokens = list(device.token_set.values_list("token", flat=True))

        self.assertEqual(len(tokens), 8)
        self.assertTrue(all(len(token) == 12 for token in tokens))
        output = out.getvalue()
        self.assertIn("Generated 8 recovery code(s)", output)
        self.assertIn("Recovery codes are hidden by default.", output)
        self.assertTrue(all(token not in output for token in tokens))

    def test_show_codes_prints_generated_codes(self):
        out = StringIO()

        call_command(
            "generate_2fa_recovery_codes",
            "--target-email",
            self.user.email,
            "--count",
            "3",
            "--show-codes",
            stdout=out,
        )

        device = StaticDevice.objects.get(user=self.user)
        tokens = list(device.token_set.values_list("token", flat=True))
        output = out.getvalue()

        self.assertEqual(len(tokens), 3)
        self.assertTrue(all(token in output for token in tokens))

    def test_regeneration_rotates_existing_codes(self):
        first_out = StringIO()
        second_out = StringIO()

        call_command(
            "generate_2fa_recovery_codes",
            "--target-email",
            self.user.email,
            "--count",
            "4",
            stdout=first_out,
        )
        first_device = StaticDevice.objects.get(user=self.user)
        first_codes = set(first_device.token_set.values_list("token", flat=True))

        call_command(
            "generate_2fa_recovery_codes",
            "--target-email",
            self.user.email,
            "--count",
            "4",
            stdout=second_out,
        )

        devices = StaticDevice.objects.filter(user=self.user)
        self.assertEqual(devices.count(), 1)

        second_device = devices.first()
        second_codes = set(second_device.token_set.values_list("token", flat=True))
        self.assertNotEqual(first_codes, second_codes)
