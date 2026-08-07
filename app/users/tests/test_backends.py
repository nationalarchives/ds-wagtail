from django.contrib.auth import get_user_model
from django.test import TestCase

from app.users.backends import EmailModelBackend


class EmailModelBackendTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.backend = EmailModelBackend()
        self.user = self.user_model.objects.create_user(
            username="test.user",
            email="test.user@example.com",
            password="super-secure-password",
        )

    def test_authenticate_accepts_email_case_insensitively(self):
        user = self.backend.authenticate(
            request=None,
            username="TEST.USER@example.com",
            password="super-secure-password",
        )

        self.assertEqual(user, self.user)

    def test_authenticate_rejects_unknown_email(self):
        user = self.backend.authenticate(
            request=None,
            username="missing@example.com",
            password="super-secure-password",
        )

        self.assertIsNone(user)

    def test_authenticate_rejects_invalid_password(self):
        user = self.backend.authenticate(
            request=None,
            username="test.user@example.com",
            password="wrong-password",
        )

        self.assertIsNone(user)
