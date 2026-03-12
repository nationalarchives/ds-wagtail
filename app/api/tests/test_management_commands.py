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


class ManageAPITokenCommandShowTests(TestCase):
    def test_show_token_no_name(self):
        """Test showing a new API token with no identifier."""
        out = StringIO()
        with self.assertRaises(CommandError) as cm:
            call_command("manage_api_token", "--show", stdout=out)
            self.assertEqual(
                cm.exception, CommandError("Identifier (token name) is required")
            )
        self.assertEqual(APIToken.objects.count(), 0)

    def test_show_token(self):
        """Test showing an existing API token."""
        token = APIToken.objects.create(name="test-service")
        out = StringIO()
        call_command("manage_api_token", "test-service", "--show", stdout=out)

        self.assertEqual(APIToken.objects.count(), 1)
        self.assertIsNotNone(token)
        if token is not None:
            self.assertIsNotNone(token.key)
            self.assertTrue(len(token.key) > 0)
            self.assertEqual(token.name, "test-service")
            self.assertTrue(token.active)

            output = out.getvalue()
            self.assertIn("API token for test-service", output)
            self.assertIn(token.key, output)

    def test_show_token_quiet(self):
        """Test showing an existing API token without human-readable output."""
        token = APIToken.objects.create(name="test-service")
        out = StringIO()
        call_command(
            "manage_api_token", "test-service", "--show", "--quiet", stdout=out
        )

        self.assertEqual(APIToken.objects.count(), 1)
        self.assertIsNotNone(token)
        if token is not None:
            self.assertIsNotNone(token)
            self.assertEqual(token.name, "test-service")
            self.assertTrue(token.active)

            output = out.getvalue()
            self.assertNotIn("API token for test-service", output)
            self.assertIn(token.key, output)

    def test_show_nonexistent_token_raises_exception(self):
        """Test showing a non-existent token shows error."""
        out = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command("manage_api_token", "nonexistent", "--show", stdout=out)
            self.assertEqual(
                cm.exception, CommandError("No API token found for nonexistent")
            )


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


class ManageAPITokenCommandEnableDisableTests(TestCase):
    def test_enable_token(self):
        """Test enabling a token by name."""
        APIToken.objects.create(name="test-service", active=False)
        out = StringIO()

        call_command("manage_api_token", "test-service", "--enable", stdout=out)

        token = APIToken.objects.get(name="test-service")
        self.assertTrue(token.active)
        output = out.getvalue()
        self.assertIn("Enabled API token for test-service", output)

    def test_enable_token_already_active(self):
        """Test enabling a token that is already active."""
        APIToken.objects.create(name="test-service", active=True)
        out = StringIO()

        call_command("manage_api_token", "test-service", "--enable", stdout=out)

        token = APIToken.objects.get(name="test-service")
        self.assertTrue(token.active)
        output = out.getvalue()
        self.assertIn("Enabled API token for test-service", output)

    def test_disable_token(self):
        """Test disabling a token by name."""
        APIToken.objects.create(name="test-service", active=True)
        out = StringIO()

        call_command("manage_api_token", "test-service", "--disable", stdout=out)

        token = APIToken.objects.get(name="test-service")
        self.assertFalse(token.active)
        output = out.getvalue()
        self.assertIn("Disabled API token for test-service", output)

    def test_disable_token_already_inactive(self):
        """Test disabling a token that is already inactive."""
        APIToken.objects.create(name="test-service", active=False)
        out = StringIO()

        call_command("manage_api_token", "test-service", "--disable", stdout=out)

        token = APIToken.objects.get(name="test-service")
        self.assertFalse(token.active)
        output = out.getvalue()
        self.assertIn("Disabled API token for test-service", output)

    def test_enable_token_quiet(self):
        """Test enabling a token by name."""
        APIToken.objects.create(name="test-service", active=False)
        out = StringIO()

        call_command(
            "manage_api_token", "test-service", "--enable", "--quiet", stdout=out
        )

        token = APIToken.objects.get(name="test-service")
        self.assertTrue(token.active)
        output = out.getvalue()
        self.assertEqual("", output)

    def test_disable_token_quiet(self):
        """Test disabling a token by name."""
        APIToken.objects.create(name="test-service", active=True)
        out = StringIO()

        call_command(
            "manage_api_token", "test-service", "--disable", "--quiet", stdout=out
        )

        token = APIToken.objects.get(name="test-service")
        self.assertFalse(token.active)
        output = out.getvalue()
        self.assertEqual("", output)

    def test_enable_token_no_name(self):
        """Test enabling an API token with no identifier."""
        out = StringIO()
        with self.assertRaises(CommandError) as cm:
            call_command("manage_api_token", "--enable", stdout=out)
            self.assertEqual(
                cm.exception, CommandError("Identifier (token name) is required")
            )

    def test_disable_token_no_name(self):
        """Test disabling an API token with no identifier."""
        out = StringIO()
        with self.assertRaises(CommandError) as cm:
            call_command("manage_api_token", "--disable", stdout=out)
            self.assertEqual(
                cm.exception, CommandError("Identifier (token name) is required")
            )

    def test_enable_nonexistent_token_raises_exception(self):
        """Test enabling a non-existent token shows error."""
        out = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command("manage_api_token", "nonexistent", "--enable", stdout=out)
            self.assertEqual(
                cm.exception, CommandError("No API token found for nonexistent")
            )

    def test_disable_nonexistent_token_raises_exception(self):
        """Test disabling a non-existent token shows error."""
        out = StringIO()

        with self.assertRaises(CommandError) as cm:
            call_command("manage_api_token", "nonexistent", "--disable", stdout=out)
            self.assertEqual(
                cm.exception, CommandError("No API token found for nonexistent")
            )


class ManageAPITokenCommandListTests(TestCase):
    def test_list_tokens_no_tokens(self):
        """Test listing tokens when none exist."""
        out = StringIO()
        call_command("list_api_tokens", stdout=out)

        output = out.getvalue()
        self.assertIn("No API tokens found.", output)

    def test_list_tokens(self):
        """Test listing existing tokens."""
        APIToken.objects.create(name="service-1")
        APIToken.objects.create(name="service-2")
        APIToken.objects.create(name="service-3")

        out = StringIO()
        call_command("list_api_tokens", stdout=out)

        output = out.getvalue()
        self.assertIn("API tokens:", output)
        self.assertIn("- service-1", output)
        self.assertIn("- service-2", output)
        self.assertIn("- service-3", output)

    def test_list_tokens_quiet(self):
        """Test listing existing tokens without human-readable output."""
        APIToken.objects.create(name="service-1")
        APIToken.objects.create(name="service-2")
        APIToken.objects.create(name="service-3")

        out = StringIO()
        call_command("list_api_tokens", "--quiet", stdout=out)

        output = out.getvalue()
        self.assertNotIn("API tokens:", output)
        self.assertIn("- service-1", output)
        self.assertIn("- service-2", output)
        self.assertIn("- service-3", output)
