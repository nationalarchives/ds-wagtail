from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from app.core.forms import auth


class EmailHelpersTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="email-user",
            email="email@example.com",
            password="password",
        )

    def test_send_template_email_jinja_dry_run(self):
        subject = "Test subject"
        plain_tpl = (
            "wagtailadmin/account/recovery_codes/recovery_codes_reset_email_plain.txt"
        )
        html_tpl = "wagtailadmin/account/recovery_codes/recovery_codes_reset_email.html"
        ctx = {"user": self.user, "reason": "unit-test"}

        result = auth.send_template_email(
            self.user.email, subject, plain_tpl, html_tpl, ctx, execute=False
        )

        self.assertIsInstance(result, dict)
        self.assertFalse(result.get("sent"))
        self.assertEqual(result.get("subject"), subject)
        self.assertEqual(result.get("reason"), "unit-test")

    def test_send_template_email_fallback_to_loader(self):
        subject = "Fallback subject"
        plain_tpl = (
            "wagtailadmin/account/recovery_codes/recovery_codes_reset_email_plain.txt"
        )
        html_tpl = "wagtailadmin/account/recovery_codes/recovery_codes_reset_email.html"
        ctx = {"user": self.user, "reason": "fallback"}

        # Force engines lookup to fail so code uses Django loader fallback
        with patch("app.core.forms.auth.engines.__getitem__", side_effect=Exception()):
            result = auth.send_template_email(
                self.user.email, subject, plain_tpl, html_tpl, ctx, execute=False
            )

        self.assertIsInstance(result, dict)
        self.assertFalse(result.get("sent"))
        self.assertEqual(result.get("subject"), subject)
        self.assertEqual(result.get("reason"), "fallback")

    @patch("app.core.forms.auth.EmailMultiAlternatives.send")
    def test_send_template_email_execute_sends(self, mock_send):
        subject = "Send subject"
        plain_tpl = (
            "wagtailadmin/account/recovery_codes/recovery_codes_reset_email_plain.txt"
        )
        html_tpl = "wagtailadmin/account/recovery_codes/recovery_codes_reset_email.html"
        ctx = {"user": self.user}

        result = auth.send_template_email(
            self.user.email, subject, plain_tpl, html_tpl, ctx, execute=True
        )

        self.assertTrue(mock_send.called)
        self.assertTrue(result.get("sent"))
        self.assertEqual(result.get("subject"), subject)

    def test_send_recovery_codes_email_wraps_send_template(self):
        with patch("app.core.forms.auth.send_template_email") as mock_send:
            mock_send.return_value = {"sent": False, "subject": "s", "reason": "r"}
            res = auth.send_recovery_codes_email(self.user, reason="r", execute=False)

        self.assertEqual(res.get("reason"), "r")
        mock_send.assert_called()
