from app.api.auth import CustomTokenAuthentication, TokenUser
from app.api.models import APIToken
from django.test import RequestFactory, TestCase
from rest_framework import exceptions


class TokenUserTests(TestCase):
    def test_token_user_attributes(self):
        """Test TokenUser has correct authentication attributes."""
        token = APIToken.objects.create(name="test-token")
        user = TokenUser(token)

        self.assertTrue(user.is_authenticated)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_anonymous)
        self.assertEqual(user.token, token)

    def test_token_user_string_representation(self):
        """Test TokenUser string representation."""
        token = APIToken.objects.create(name="test-service")
        user = TokenUser(token)

        self.assertEqual(str(user), "TokenUser(test-service)")


class CustomTokenAuthenticationTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.auth = CustomTokenAuthentication()
        self.active_token = APIToken.objects.create(name="active-service", active=True)
        self.inactive_token = APIToken.objects.create(
            name="inactive-service", active=False
        )

    def test_authenticate_with_valid_token(self):
        """Test authentication succeeds with valid active token."""
        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"Token {self.active_token.key}"

        result = self.auth.authenticate(request)

        self.assertIsNotNone(result)
        user, token = result
        self.assertIsInstance(user, TokenUser)
        self.assertEqual(token, self.active_token)
        self.assertTrue(user.is_authenticated)

    def test_authenticate_with_no_token(self):
        """Test authentication returns None when no token provided."""
        request = self.factory.get("/")

        result = self.auth.authenticate(request)

        self.assertIsNone(result)

    def test_authenticate_with_invalid_keyword(self):
        """Test authentication returns None with wrong keyword."""
        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {self.active_token.key}"

        result = self.auth.authenticate(request)

        self.assertIsNone(result)

    def test_authenticate_with_missing_credentials(self):
        """Test authentication fails when only keyword provided."""
        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Token"

        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.auth.authenticate(request)

        self.assertIn("No credentials provided", str(context.exception))

    def test_authenticate_with_spaces_in_token(self):
        """Test authentication fails with spaces in token."""
        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Token abc def 123"

        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.auth.authenticate(request)

        self.assertIn("should not contain spaces", str(context.exception))

    def test_authenticate_with_nonexistent_token(self):
        """Test authentication fails with non-existent token key."""
        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Token nonexistent-key-12345"

        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.auth.authenticate(request)

        self.assertIn("Invalid token", str(context.exception))

    def test_authenticate_with_inactive_token(self):
        """Test authentication fails with inactive token."""
        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"Token {self.inactive_token.key}"

        with self.assertRaises(exceptions.PermissionDenied) as context:
            self.auth.authenticate(request)

        self.assertIn("inactive or deleted", str(context.exception))

    def test_authenticate_credentials_returns_token_user(self):
        """Test authenticate_credentials returns TokenUser instance."""
        user, token = self.auth.authenticate_credentials(str(self.active_token.key))

        self.assertIsInstance(user, TokenUser)
        self.assertEqual(token, self.active_token)
        self.assertEqual(user.token, self.active_token)

    def test_get_model_returns_api_token(self):
        """Test get_model returns APIToken model."""
        model = self.auth.get_model()

        self.assertEqual(model, APIToken)
