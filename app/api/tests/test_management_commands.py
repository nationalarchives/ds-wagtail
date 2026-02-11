from io import StringIO

from app.api.models import APIToken
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class ManageAPITokenCommandCreateTests(TestCase):
    def test_create_token_no_name(self):
        """Test creating a new API token with no identifier."""
        out = StringIO()
        with self.assertRaises(CommandError) as cm:
            call_command("manage_api_token", stdout=out)
            self.assertEqual(
                cm.exception, CommandError("Identifier (token name) is required")
            )
        self.assertEqual(APIToken.objects.count(), 0)

    def test_create_token(self):
        """Test creating a new API token."""
        out = StringIO()
        call_command("manage_api_token", "test-service", stdout=out)

        self.assertEqual(APIToken.objects.count(), 1)
        token = APIToken.objects.first()
        self.assertIsNotNone(token)
        if token is not None:
            self.assertIsNotNone(token.key)
            self.assertTrue(len(token.key) > 0)
            self.assertEqual(token.name, "test-service")
            self.assertTrue(token.active)

            output = out.getvalue()
            self.assertIn("Created API token for test-service", output)
            self.assertIn(token.key, output)

    def test_create_token_quiet(self):
        """Test creating a new API token without human-readable output."""
        out = StringIO()
        call_command("manage_api_token", "test-service", "--quiet", stdout=out)

        self.assertEqual(APIToken.objects.count(), 1)
        token = APIToken.objects.first()
        self.assertIsNotNone(token)
        if token is not None:
            self.assertIsNotNone(token)
            self.assertEqual(token.name, "test-service")
            self.assertTrue(token.active)

            output = out.getvalue()
            self.assertNotIn("Created API token for test-service", output)
            self.assertIn(token.key, output)

    def test_create_duplicate_token_raises_exception(self):
        """Test creating a token with duplicate name returns existing key."""
        APIToken.objects.create(name="test-service")
        out = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command("manage_api_token", "test-service", stdout=out)
            self.assertEqual(
                cm.exception,
                CommandError(
                    "API token already exists for test-service, use --refresh to regenerate"
                ),
            )

        # Should still only have 1 token
        self.assertEqual(APIToken.objects.count(), 1)

    def test_multiple_tokens_can_exist(self):
        """Test creating multiple tokens."""
        call_command("manage_api_token", "service-1")
        call_command("manage_api_token", "service-2")
        call_command("manage_api_token", "service-3")

        self.assertEqual(APIToken.objects.count(), 3)
        names = list(APIToken.objects.values_list("name", flat=True))
        self.assertIn("service-1", names)
        self.assertIn("service-2", names)
        self.assertIn("service-3", names)


class ManageAPITokenCommandRefreshTests(TestCase):
    def test_refresh_token_no_name(self):
        """Test creating a new API token with no identifier."""
        out = StringIO()
        with self.assertRaises(CommandError) as cm:
            call_command("manage_api_token", "--refresh", stdout=out)
            self.assertEqual(
                cm.exception, CommandError("Identifier (token name) is required")
            )
        self.assertEqual(APIToken.objects.count(), 0)

    def test_refresh_existing_token(self):
        """Test refreshing an existing token regenerates the key."""
        token = APIToken.objects.create(name="test-service")
        old_key = token.key
        out = StringIO()

        call_command("manage_api_token", "test-service", "--refresh", stdout=out)

        # Should still have 1 token
        self.assertEqual(APIToken.objects.count(), 1)
        token.refresh_from_db()
        new_key = token.key

        # Key should have changed
        self.assertNotEqual(old_key, new_key)

        output = out.getvalue()
        self.assertIn("Refreshed API token for test-service", output)
        self.assertNotIn(old_key, output)
        self.assertIn(new_key, output)

    def test_refresh_existing_token_quiet(self):
        """Test refreshing an existing token regenerates the key."""
        token = APIToken.objects.create(name="test-service")
        old_key = token.key
        out = StringIO()

        call_command(
            "manage_api_token", "test-service", "--refresh", "--quiet", stdout=out
        )

        # Should still have 1 token
        self.assertEqual(APIToken.objects.count(), 1)
        token.refresh_from_db()
        new_key = token.key

        # Key should have changed
        self.assertNotEqual(old_key, new_key)

        output = out.getvalue()
        self.assertNotIn("Refreshed API token for test-service", output)
        self.assertNotIn(old_key, output)
        self.assertIn(new_key, output)

    def test_refresh_nonexistent_token_creates_it(self):
        """Test refreshing a non-existent token creates it."""
        out = StringIO()

        call_command("manage_api_token", "new-service", "--refresh", stdout=out)

        self.assertEqual(APIToken.objects.count(), 1)
        token = APIToken.objects.get(name="new-service")

        output = out.getvalue()
        self.assertIn("Created API token for new-service", output)
        self.assertIn(token.key, output)

    def test_refresh_nonexistent_token_creates_it_quiet(self):
        """Test refreshing a non-existent token creates it."""
        out = StringIO()

        call_command(
            "manage_api_token", "new-service", "--refresh", "--quiet", stdout=out
        )

        self.assertEqual(APIToken.objects.count(), 1)
        token = APIToken.objects.get(name="new-service")

        output = out.getvalue()
        self.assertNotIn("Created API token for new-service", output)
        self.assertIn(token.key, output)


class ManageAPITokenCommandDeleteTests(TestCase):
    def test_delete_token_no_name(self):
        """Test deleteing an API token with no identifier."""
        out = StringIO()
        with self.assertRaises(CommandError) as cm:
            call_command("manage_api_token", "--delete", stdout=out)
            self.assertEqual(
                cm.exception, CommandError("Identifier (token name) is required")
            )

    def test_delete_token(self):
        """Test deleting a token by name."""
        APIToken.objects.create(name="test-service")
        out = StringIO()

        call_command("manage_api_token", "test-service", "--delete", stdout=out)

        self.assertEqual(APIToken.objects.count(), 0)
        output = out.getvalue()
        self.assertIn("Deleted API token for test-service", output)

    def test_delete_token_quiet(self):
        """Test deleting a token by name."""
        APIToken.objects.create(name="test-service")
        out = StringIO()

        call_command(
            "manage_api_token", "test-service", "--delete", "--quiet", stdout=out
        )

        self.assertEqual(APIToken.objects.count(), 0)
        output = out.getvalue()
        self.assertEqual("", output)

    def test_delete_nonexistent_token_raises_exception(self):
        """Test deleting a non-existent token shows error."""
        out = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command("manage_api_token", "nonexistent", "--delete", stdout=out)
            self.assertEqual(
                cm.exception, CommandError("No API token found for nonexistent")
            )
