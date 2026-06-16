from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class Manage2FADevicesCommandTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="old-password-123",
        )

    def test_target_user_not_found_raises_command_error(self):
        out = StringIO()

        with self.assertRaises(CommandError):
            call_command(
                "manage_2fa_devices",
                "--target-email",
                "missing@example.com",
                stdout=out,
            )

    def test_dry_run_does_not_reset_password_and_prints_reason(self):
        out = StringIO()

        call_command(
            "manage_2fa_devices",
            "--target-email",
            self.user.email,
            "--reason",
            "Compromised device reported",
            stdout=out,
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("old-password-123"))

        output = out.getvalue()
        self.assertIn(
            "DRY RUN: would reset the user's password to a random value.", output
        )
        self.assertIn("Compromised device reported", output)

    @patch("app.api.management.commands.manage_2fa_devices.HtmlPasswordResetForm.save")
    def test_execute_resets_password_and_passes_reason_to_form_save(self, save_mock):
        out = StringIO()

        call_command(
            "manage_2fa_devices",
            "--target-email",
            self.user.email,
            "--reason",
            "Security team request",
            "--execute",
            stdout=out,
        )

        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password("old-password-123"))

        self.assertTrue(save_mock.called)
        _, kwargs = save_mock.call_args
        self.assertEqual(
            kwargs.get("extra_email_context"), {"reason": "Security team request"}
        )

    @patch("app.api.management.commands.manage_2fa_devices.HtmlPasswordResetForm.save")
    def test_execute_with_no_reason_passes_empty_extra_context(self, save_mock):
        out = StringIO()

        call_command(
            "manage_2fa_devices",
            "--target-email",
            self.user.email,
            "--execute",
            stdout=out,
        )

        self.assertTrue(save_mock.called)
        _, kwargs = save_mock.call_args
        self.assertEqual(kwargs.get("extra_email_context"), {})
