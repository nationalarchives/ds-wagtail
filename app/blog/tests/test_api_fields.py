from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from wagtail.models import Site

from ..factories import (
    BlogIndexPageFactory,
    BlogPageFactory,
    BlogPostPageFactory,
)


class TestBlogIndexPageAPIFields(TestCase):
    """Tests for BlogIndexPage API fields availability"""

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

        self.blog_post = BlogPostPageFactory(
            title="Blog Post",
            parent=self.blog_page,
            live=True,
            published_date=datetime(2024, 1, 15, tzinfo=timezone.UTC),
        )

    def test_blog_index_page_has_top_blogs_api_field(self):
        """Test that BlogIndexPage has top_blogs in api_fields"""
        api_fields = self.blog_index_page.api_fields
        field_names = [field.name for field in api_fields]
        self.assertIn("top_blogs", field_names)

    def test_blog_index_page_has_blog_posts_count_api_field(self):
        """Test that BlogIndexPage has blog_posts_count in api_fields"""
        api_fields = self.blog_index_page.api_fields
        field_names = [field.name for field in api_fields]
        self.assertIn("blog_posts_count", field_names)

    def test_blog_index_page_has_blog_posts_authors_api_field(self):
        """Test that BlogIndexPage has blog_posts_authors in api_fields"""
        api_fields = self.blog_index_page.api_fields
        field_names = [field.name for field in api_fields]
        self.assertIn("blog_posts_authors", field_names)

    def test_blog_index_page_has_blogs_feeds_page_api_field(self):
        """Test that BlogIndexPage has blogs_feeds_page in api_fields"""
        api_fields = self.blog_index_page.api_fields
        field_names = [field.name for field in api_fields]
        self.assertIn("blogs_feeds_page", field_names)

    def test_blog_index_page_top_blogs_serializer_is_many(self):
        """Test that top_blogs field uses many=True serializer"""
        api_fields = self.blog_index_page.api_fields
        top_blogs_field = next((f for f in api_fields if f.name == "top_blogs"), None)
        self.assertIsNotNone(top_blogs_field)
        self.assertIsNotNone(top_blogs_field.serializer)

    def test_blog_index_page_blog_posts_authors_has_serializer(self):
        """Test that blog_posts_authors field has the correct serializer"""
        api_fields = self.blog_index_page.api_fields
        authors_field = next(
            (f for f in api_fields if f.name == "blog_posts_authors"), None
        )
        self.assertIsNotNone(authors_field)
        self.assertIsNotNone(authors_field.serializer)


class TestBlogPageAPIFields(TestCase):
    """Tests for BlogPage API fields availability"""

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

        self.child_blog = BlogPageFactory(
            title="Child Blog",
            parent=self.blog_page,
            live=True,
        )

        self.blog_post = BlogPostPageFactory(
            title="Blog Post",
            parent=self.blog_page,
            live=True,
            published_date=datetime(2024, 1, 15, tzinfo=timezone.UTC),
        )

    def test_blog_page_has_child_blogs_api_field(self):
        """Test that BlogPage has child_blogs in api_fields"""
        api_fields = self.blog_page.api_fields
        field_names = [field.name for field in api_fields]
        self.assertIn("child_blogs", field_names)

    def test_blog_page_has_blog_posts_count_api_field(self):
        """Test that BlogPage has blog_posts_count in api_fields"""
        api_fields = self.blog_page.api_fields
        field_names = [field.name for field in api_fields]
        self.assertIn("blog_posts_count", field_names)

    def test_blog_page_has_blog_posts_authors_api_field(self):
        """Test that BlogPage has blog_posts_authors in api_fields"""
        api_fields = self.blog_page.api_fields
        field_names = [field.name for field in api_fields]
        self.assertIn("blog_posts_authors", field_names)

    def test_blog_page_has_blogs_feeds_page_api_field(self):
        """Test that BlogPage has blogs_feeds_page in api_fields"""
        api_fields = self.blog_page.api_fields
        field_names = [field.name for field in api_fields]
        self.assertIn("blogs_feeds_page", field_names)

    def test_blog_page_child_blogs_serializer_is_many(self):
        """Test that child_blogs field uses many=True serializer"""
        api_fields = self.blog_page.api_fields
        child_blogs_field = next(
            (f for f in api_fields if f.name == "child_blogs"), None
        )
        self.assertIsNotNone(child_blogs_field)
        self.assertIsNotNone(child_blogs_field.serializer)

    def test_blog_page_blog_posts_authors_has_serializer(self):
        """Test that blog_posts_authors field has the correct serializer"""
        api_fields = self.blog_page.api_fields
        authors_field = next(
            (f for f in api_fields if f.name == "blog_posts_authors"), None
        )
        self.assertIsNotNone(authors_field)
        self.assertIsNotNone(authors_field.serializer)

    def test_blog_page_has_custom_type_label_api_field(self):
        """Test that BlogPage has custom_type_label in api_fields"""
        api_fields = self.blog_page.api_fields
        field_names = [field.name for field in api_fields]
        self.assertIn("custom_type_label", field_names)
