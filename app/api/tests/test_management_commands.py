from io import StringIO
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from app.api.models import APIToken


class ManageAPITokenCommandTests(TestCase):
    def test_create_token(self):
        """Test creating a new API token."""
        out = StringIO()
        call_command('manage_api_token', 'test-service', stdout=out)
        
        self.assertEqual(APIToken.objects.count(), 1)
        token = APIToken.objects.first()
        self.assertEqual(token.name, 'test-service')
        self.assertTrue(token.active)
        
        output = out.getvalue()
        self.assertIn('Successfully created API token: test-service', output)
        self.assertIn('API Key:', output)
        self.assertIn(str(token.key), output)
    
    def test_create_duplicate_token_returns_existing(self):
        """Test creating a token with duplicate name returns existing key."""
        token = APIToken.objects.create(name='test-service')
        existing_key = str(token.key)
        out = StringIO()
        
        call_command('manage_api_token', 'test-service', stdout=out)
        
        # Should still only have 1 token
        self.assertEqual(APIToken.objects.count(), 1)
        output = out.getvalue()
        self.assertIn('Token already exists: test-service', output)
        self.assertIn(existing_key, output)
    
    def test_delete_token_by_name(self):
        """Test deleting a token by name."""
        token = APIToken.objects.create(name='test-service')
        out = StringIO()
        
        call_command('manage_api_token', 'test-service', '--delete', stdout=out)
        
        self.assertEqual(APIToken.objects.count(), 0)
        output = out.getvalue()
        self.assertIn('Successfully deleted API token: test-service', output)
    
    def test_delete_token_by_key(self):
        """Test deleting a token by key."""
        token = APIToken.objects.create(name='test-service')
        token_key = str(token.key)
        out = StringIO()
        
        call_command('manage_api_token', token_key, '--delete', stdout=out)
        
        self.assertEqual(APIToken.objects.count(), 0)
        output = out.getvalue()
        self.assertIn('Successfully deleted API token: test-service', output)
    
    def test_delete_nonexistent_token(self):
        """Test deleting a non-existent token shows error."""
        out = StringIO()
        
        call_command('manage_api_token', 'nonexistent', '--delete', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Token not found: nonexistent', output)
    
    def test_delete_prefers_name_over_key(self):
        """Test that deletion searches by name first, then key."""
        # Create token with a UUID-like name
        token1 = APIToken.objects.create(name='abc-123-def')
        token2 = APIToken.objects.create(name='service-2')
        
        out = StringIO()
        call_command('manage_api_token', 'abc-123-def', '--delete', stdout=out)
        
        # Should delete token1 (by name match), not token2
        self.assertFalse(APIToken.objects.filter(name='abc-123-def').exists())
        self.assertTrue(APIToken.objects.filter(name='service-2').exists())
    
    def test_token_key_is_generated(self):
        """Test that token key is automatically generated."""
        out = StringIO()
        call_command('manage_api_token', 'test-service', stdout=out)
        
        token = APIToken.objects.get(name='test-service')
        self.assertIsNotNone(token.key)
        self.assertTrue(len(str(token.key)) > 0)
    
    def test_multiple_tokens_can_exist(self):
        """Test creating multiple tokens."""
        call_command('manage_api_token', 'service-1')
        call_command('manage_api_token', 'service-2')
        call_command('manage_api_token', 'service-3')
        
        self.assertEqual(APIToken.objects.count(), 3)
        names = list(APIToken.objects.values_list('name', flat=True))
        self.assertIn('service-1', names)
        self.assertIn('service-2', names)
        self.assertIn('service-3', names)
    
    def test_refresh_existing_token(self):
        """Test refreshing an existing token regenerates the key."""
        token = APIToken.objects.create(name='test-service')
        old_key = str(token.key)
        out = StringIO()
        
        call_command('manage_api_token', 'test-service', '--refresh', stdout=out)
        
        # Should still have 1 token
        self.assertEqual(APIToken.objects.count(), 1)
        token.refresh_from_db()
        new_key = str(token.key)
        
        # Key should have changed
        self.assertNotEqual(old_key, new_key)
        
        output = out.getvalue()
        self.assertIn('Successfully refreshed API token: test-service', output)
        self.assertIn(new_key, output)
        self.assertNotIn(old_key, output)
    
    def test_refresh_nonexistent_token_creates_it(self):
        """Test refreshing a non-existent token creates it."""
        out = StringIO()
        
        call_command('manage_api_token', 'new-service', '--refresh', stdout=out)
        
        self.assertEqual(APIToken.objects.count(), 1)
        token = APIToken.objects.get(name='new-service')
        
        output = out.getvalue()
        self.assertIn('Successfully created API token: new-service', output)
        self.assertIn(str(token.key), output)
    
    def test_refresh_outputs_new_key(self):
        """Test that refresh command outputs the new key."""
        APIToken.objects.create(name='test-service')
        out = StringIO()
        
        call_command('manage_api_token', 'test-service', '--refresh', stdout=out)
        
        output = out.getvalue()
        self.assertIn('API Key:', output)
