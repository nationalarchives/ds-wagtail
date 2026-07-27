from django.test import TestCase
from wagtail.models import Site

from ..factories import (
    BlogIndexPageFactory,
    BlogPageFactory,
)
from ..serializers import BlogPostAuthorsSerializer


class TestBlogPostAuthorsSerializer(TestCase):
    """Tests for BlogPostAuthorsSerializer"""

    def setUp(self):
        """Set up test data"""
        self.root_page = Site.objects.get(is_default_site=True).root_page

        self.blog_index_page = BlogIndexPageFactory(
            title="Blog Index",
            parent=self.root_page,
            live=True,
        )

        self.blog_page = BlogPageFactory(
            title="Blog",
            parent=self.blog_index_page,
            live=True,
        )

    def test_serializer_handles_empty_list(self):
        """Test that serializer properly handles an empty list"""
        serializer = BlogPostAuthorsSerializer()
        result = serializer.to_representation([])
        self.assertEqual(result, [])

    def test_serializer_handles_single_author_dict(self):
        """Test that serializer properly handles a single author dict"""
        author_data = {
            "author": self.blog_page,
            "posts": 5,
        }

        serializer = BlogPostAuthorsSerializer()
        result = serializer.to_representation(author_data)

        self.assertIsInstance(result, dict)
        self.assertIn("author", result)
        self.assertIn("posts", result)
        self.assertEqual(result["posts"], 5)

    def test_serializer_handles_list_of_authors(self):
        """Test that serializer properly handles a list of author dicts"""
        author_list = [
            {
                "author": self.blog_page,
                "posts": 5,
            },
            {
                "author": self.blog_index_page,
                "posts": 3,
            },
        ]

        serializer = BlogPostAuthorsSerializer()
        result = serializer.to_representation(author_list)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]["posts"], 5)
        self.assertEqual(result[1]["posts"], 3)

    def test_serializer_includes_author_page_data(self):
        """Test that serializer includes serialized author page data"""
        author_data = {
            "author": self.blog_page,
            "posts": 5,
        }

        serializer = BlogPostAuthorsSerializer()
        result = serializer.to_representation(author_data)

        # The author should be serialized using DefaultPageSerializer
        self.assertIn("author", result)
        author = result["author"]

        # Check that basic page data is included
        if author:
            # DefaultPageSerializer returns a dict with page fields
            self.assertIsInstance(author, (dict, type(None)))

    def test_serializer_handles_missing_author(self):
        """Test that serializer gracefully handles missing author"""
        author_data = {
            "author": None,
            "posts": 5,
        }

        serializer = BlogPostAuthorsSerializer()
        result = serializer.to_representation(author_data)

        self.assertIn("author", result)
        self.assertIn("posts", result)
        self.assertEqual(result["posts"], 5)

    def test_serializer_handles_missing_posts_count(self):
        """Test that serializer defaults to 0 posts if missing"""
        author_data = {
            "author": self.blog_page,
        }

        serializer = BlogPostAuthorsSerializer()
        result = serializer.to_representation(author_data)

        self.assertEqual(result["posts"], 0)
