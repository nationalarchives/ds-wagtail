from io import StringIO
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
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

    @patch("app.api.management.commands.manage_2fa_devices.HtmlPasswordResetForm.save")
    @patch("app.api.management.commands.manage_2fa_devices.TOTPDevice.objects.filter")
    def test_execute_deletes_2fa_devices(self, device_filter_mock, save_mock):
        out = StringIO()

        devices_qs = MagicMock()
        devices_qs.count.side_effect = [2, 0]
        devices_qs.__iter__.return_value = iter([])
        devices_qs.delete.return_value = (2, {})
        device_filter_mock.return_value = devices_qs

        call_command(
            "manage_2fa_devices",
            "--target-email",
            self.user.email,
            "--execute",
            stdout=out,
        )

        devices_qs.delete.assert_called_once()
        self.assertEqual(devices_qs.count(), 0)
        self.assertTrue(save_mock.called)

    @patch("app.api.management.commands.manage_2fa_devices.HtmlPasswordResetForm.save")
    @patch("app.api.management.commands.manage_2fa_devices.TOTPDevice.objects.filter")
    def test_dry_run_does_not_delete_2fa_devices(self, device_filter_mock, save_mock):
        out = StringIO()

        devices_qs = MagicMock()
        devices_qs.count.return_value = 2
        devices_qs.__iter__.return_value = iter([])
        devices_qs.delete.return_value = (2, {})
        device_filter_mock.return_value = devices_qs

        call_command(
            "manage_2fa_devices",
            "--target-email",
            self.user.email,
            stdout=out,
        )

        devices_qs.delete.assert_not_called()
        self.assertEqual(devices_qs.count(), 2)
        self.assertTrue(save_mock.called)

    @patch("app.api.management.commands.manage_2fa_devices.HtmlPasswordResetForm.save")
    @patch("app.api.management.commands.manage_2fa_devices.Session.objects.filter")
    def test_execute_revokes_user_sessions(self, session_filter_mock, save_mock):
        out = StringIO()

        matching_session = MagicMock()
        matching_session.session_key = "abc123"
        matching_session.get_decoded.return_value = {"_auth_user_id": str(self.user.pk)}

        scan_qs = [matching_session]
        revoke_qs = MagicMock()
        revoke_qs.delete.return_value = (1, {})
        session_filter_mock.side_effect = [scan_qs, revoke_qs]

        call_command(
            "manage_2fa_devices",
            "--target-email",
            self.user.email,
            "--execute",
            stdout=out,
        )

        revoke_qs.delete.assert_called_once()
        self.assertTrue(save_mock.called)

    @patch("app.api.management.commands.manage_2fa_devices.HtmlPasswordResetForm.save")
    @patch("app.api.management.commands.manage_2fa_devices.Session.objects.filter")
    def test_dry_run_does_not_revoke_sessions(self, session_filter_mock, save_mock):
        out = StringIO()

        matching_session = MagicMock()
        matching_session.session_key = "abc123"
        matching_session.get_decoded.return_value = {"_auth_user_id": str(self.user.pk)}

        scan_qs = [matching_session]
        revoke_qs = MagicMock()
        revoke_qs.delete.return_value = (1, {})
        session_filter_mock.side_effect = [scan_qs, revoke_qs]

        call_command(
            "manage_2fa_devices",
            "--target-email",
            self.user.email,
            stdout=out,
        )

        revoke_qs.delete.assert_not_called()
        self.assertTrue(save_mock.called)

    @patch("app.api.management.commands.manage_2fa_devices.HtmlPasswordResetForm.save")
    def test_execute_removes_real_user_session(self, save_mock):
        out = StringIO()

        session_store = SessionStore()
        session_store["_auth_user_id"] = str(self.user.pk)
        session_store["_auth_user_backend"] = "django.contrib.auth.backends.ModelBackend"
        session_store["_auth_user_hash"] = "test-hash"
        session_store.save()
        session_key = session_store.session_key

        self.assertTrue(Session.objects.filter(session_key=session_key).exists())

        call_command(
            "manage_2fa_devices",
            "--target-email",
            self.user.email,
            "--execute",
            stdout=out,
        )

        self.assertFalse(Session.objects.filter(session_key=session_key).exists())
        self.assertTrue(save_mock.called)
