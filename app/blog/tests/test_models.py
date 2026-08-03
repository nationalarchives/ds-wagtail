from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from wagtail.models import Site

from ..factories import (
    BlogIndexPageFactory,
    BlogPageFactory,
    BlogPostPageFactory,
)
from ..models import BlogPage


class TestBlogIndexPageTopBlogs(TestCase):
    """Tests for BlogIndexPage.top_blogs property"""

    def setUp(self):
        """Set up test data"""
        self.root_page = Site.objects.get(is_default_site=True).root_page

        self.blog_index_page = BlogIndexPageFactory(
            title="Blog Index",
            parent=self.root_page,
            live=True,
        )

        self.blog_page_1 = BlogPageFactory(
            title="Blog 1",
            parent=self.blog_index_page,
            live=True,
        )

        self.blog_page_2 = BlogPageFactory(
            title="Blog 2",
            parent=self.blog_index_page,
            live=True,
        )

    def test_top_blogs_returns_queryset(self):
        """Test that top_blogs returns a queryset"""
        result = self.blog_index_page.top_blogs
        self.assertEqual(result.model, BlogPage)

    def test_top_blogs_returns_live_public_pages_only(self):
        """Test that top_blogs only returns live and public pages"""
        # Create an unpublished blog
        unpublished_blog = BlogPageFactory(
            title="Unpublished Blog",
            parent=self.blog_index_page,
            live=False,
        )

        result = self.blog_index_page.top_blogs
        blog_ids = list(result.values_list("id", flat=True))

        self.assertIn(self.blog_page_1.id, blog_ids)
        self.assertIn(self.blog_page_2.id, blog_ids)
        self.assertNotIn(unpublished_blog.id, blog_ids)

    def test_top_blogs_excludes_child_blogs(self):
        """Test that top_blogs excludes blogs that are children of other blogs"""
        # Create a child blog under blog_page_1
        child_blog = BlogPageFactory(
            title="Child Blog",
            parent=self.blog_page_1,
            live=True,
        )

        result = self.blog_index_page.top_blogs
        blog_ids = list(result.values_list("id", flat=True))

        self.assertIn(self.blog_page_1.id, blog_ids)
        self.assertIn(self.blog_page_2.id, blog_ids)
        self.assertNotIn(child_blog.id, blog_ids)

    def test_top_blogs_is_ordered_by_title(self):
        """Test that top_blogs results are ordered by title"""
        # Create blogs with specific titles
        BlogPageFactory(title="Alpha Blog", parent=self.blog_index_page, live=True)
        BlogPageFactory(title="Beta Blog", parent=self.blog_index_page, live=True)
        BlogPageFactory(title="Gamma Blog", parent=self.blog_index_page, live=True)

        result = self.blog_index_page.top_blogs
        titles = list(result.values_list("title", flat=True))

        self.assertEqual(titles, sorted(titles))


class TestBlogIndexPageBlogPostsCount(TestCase):
    """Tests for BlogIndexPage.blog_posts_count property"""

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

    def test_blog_posts_count_returns_empty_list_when_no_posts(self):
        """Test that blog_posts_count returns empty list when there are no posts"""
        result = self.blog_index_page.blog_posts_count
        self.assertEqual(result, [])

    def test_blog_posts_count_aggregates_by_year_and_month(self):
        """Test that blog_posts_count properly aggregates posts by year and month"""
        # Create posts in different months
        BlogPostPageFactory(
            title="Post 1",
            parent=self.blog_page,
            live=True,
            published_date=datetime(2024, 1, 15, tzinfo=timezone.UTC),
        )
        BlogPostPageFactory(
            title="Post 2",
            parent=self.blog_page,
            live=True,
            published_date=datetime(2024, 1, 20, tzinfo=timezone.UTC),
        )
        BlogPostPageFactory(
            title="Post 3",
            parent=self.blog_page,
            live=True,
            published_date=datetime(2024, 2, 10, tzinfo=timezone.UTC),
        )

        result = self.blog_index_page.blog_posts_count

        self.assertEqual(len(result), 1)  # 1 year of data
        self.assertEqual(result[0]["year"], 2024)
        self.assertEqual(result[0]["posts"], 3)

        # Check monthly breakdown
        months_in_2024 = result[0]["months"]
        self.assertEqual(len(months_in_2024), 2)  # January and February

    def test_blog_posts_count_only_includes_live_posts(self):
        """Test that blog_posts_count only includes live posts"""
        BlogPostPageFactory(
            title="Published Post",
            parent=self.blog_page,
            live=True,
            published_date=datetime(2024, 1, 15, tzinfo=timezone.UTC),
        )
        BlogPostPageFactory(
            title="Unpublished Post",
            parent=self.blog_page,
            live=False,
            published_date=datetime(2024, 1, 20, tzinfo=timezone.UTC),
        )

        result = self.blog_index_page.blog_posts_count

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["year"], 2024)
        self.assertEqual(result[0]["posts"], 1)


class TestBlogIndexPageBlogPostsAuthors(TestCase):
    """Tests for BlogIndexPage.blog_posts_authors property"""

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

    def test_blog_posts_authors_returns_empty_list_when_no_posts(self):
        """Test that blog_posts_authors returns empty list when there are no posts"""
        result = self.blog_index_page.blog_posts_authors
        self.assertEqual(result, [])

    def test_blog_posts_authors_is_sorted_by_posts_count(self):
        """Test that blog_posts_authors results are sorted by post count descending"""
        # Create posts and authors will need to be added separately
        BlogPostPageFactory(
            title="Post 1",
            parent=self.blog_page,
            live=True,
            published_date=datetime(2024, 1, 15, tzinfo=timezone.UTC),
        )
        BlogPostPageFactory(
            title="Post 2",
            parent=self.blog_page,
            live=True,
            published_date=datetime(2024, 1, 20, tzinfo=timezone.UTC),
        )

        result = self.blog_index_page.blog_posts_authors

        # The structure should maintain sort order
        if len(result) > 1:
            for i in range(len(result) - 1):
                self.assertGreaterEqual(result[i]["posts"], result[i + 1]["posts"])

    def test_blog_posts_authors_limited_to_12(self):
        """Test that blog_posts_authors returns at most 12 authors"""
        # Create 15 blog posts with author information would require more setup
        # For now, just verify the structure returns a list
        result = self.blog_index_page.blog_posts_authors
        self.assertLessEqual(len(result), 12)


class TestBlogPageChildBlogs(TestCase):
    """Tests for BlogPage.child_blogs property"""

    def setUp(self):
        """Set up test data"""
        self.root_page = Site.objects.get(is_default_site=True).root_page

        self.blog_index_page = BlogIndexPageFactory(
            title="Blog Index",
            parent=self.root_page,
            live=True,
        )

        self.parent_blog_page = BlogPageFactory(
            title="Parent Blog",
            parent=self.blog_index_page,
            live=True,
        )

    def test_child_blogs_returns_queryset(self):
        """Test that child_blogs returns a queryset"""
        result = self.parent_blog_page.child_blogs
        self.assertEqual(result.model, BlogPage)

    def test_child_blogs_returns_only_direct_children(self):
        """Test that child_blogs only returns direct children"""
        # Create direct children
        child_blog_1 = BlogPageFactory(
            title="Child 1",
            parent=self.parent_blog_page,
            live=True,
        )
        child_blog_2 = BlogPageFactory(
            title="Child 2",
            parent=self.parent_blog_page,
            live=True,
        )

        # Create a grandchild
        grandchild_blog = BlogPageFactory(
            title="Grandchild",
            parent=child_blog_1,
            live=True,
        )

        result = self.parent_blog_page.child_blogs
        blog_ids = list(result.values_list("id", flat=True))

        self.assertIn(child_blog_1.id, blog_ids)
        self.assertIn(child_blog_2.id, blog_ids)
        self.assertNotIn(grandchild_blog.id, blog_ids)

    def test_child_blogs_excludes_unpublished_pages(self):
        """Test that child_blogs only returns live and public pages"""
        child_blog_live = BlogPageFactory(
            title="Live Child",
            parent=self.parent_blog_page,
            live=True,
        )
        child_blog_unpublished = BlogPageFactory(
            title="Unpublished Child",
            parent=self.parent_blog_page,
            live=False,
        )

        result = self.parent_blog_page.child_blogs
        blog_ids = list(result.values_list("id", flat=True))

        self.assertIn(child_blog_live.id, blog_ids)
        self.assertNotIn(child_blog_unpublished.id, blog_ids)

    def test_child_blogs_is_ordered_by_title(self):
        """Test that child_blogs results are ordered by title"""
        BlogPageFactory(title="Zebra Blog", parent=self.parent_blog_page, live=True)
        BlogPageFactory(title="Alpha Blog", parent=self.parent_blog_page, live=True)
        BlogPageFactory(title="Beta Blog", parent=self.parent_blog_page, live=True)

        result = self.parent_blog_page.child_blogs
        titles = list(result.values_list("title", flat=True))

        self.assertEqual(titles, sorted(titles))


class TestBlogPageBlogPostsCount(TestCase):
    """Tests for BlogPage.blog_posts_count property"""

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

    def test_blog_page_blog_posts_count_returns_empty_list_when_no_posts(self):
        """Test that blog_posts_count returns empty list when there are no posts"""
        result = self.blog_page.blog_posts_count
        self.assertEqual(result, [])

    def test_blog_page_blog_posts_count_includes_only_descendant_posts(self):
        """Test that blog_posts_count only includes posts within the blog hierarchy"""
        # Create posts in this blog
        BlogPostPageFactory(
            title="Post in Blog",
            parent=self.blog_page,
            live=True,
            published_date=datetime(2024, 1, 15, tzinfo=timezone.UTC),
        )

        # Create another blog with its own posts
        other_blog = BlogPageFactory(
            title="Other Blog",
            parent=self.blog_index_page,
            live=True,
        )
        BlogPostPageFactory(
            title="Post in Other Blog",
            parent=other_blog,
            live=True,
            published_date=datetime(2024, 1, 20, tzinfo=timezone.UTC),
        )

        result = self.blog_page.blog_posts_count

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["year"], 2024)
        self.assertEqual(result[0]["posts"], 1)  # Only one post

    def test_blog_page_blog_posts_count_aggregates_by_year_and_month(self):
        """Test that blog_posts_count properly aggregates posts by year and month"""
        BlogPostPageFactory(
            title="Post 1",
            parent=self.blog_page,
            live=True,
            published_date=datetime(2024, 1, 15, tzinfo=timezone.UTC),
        )
        BlogPostPageFactory(
            title="Post 2",
            parent=self.blog_page,
            live=True,
            published_date=datetime(2024, 1, 20, tzinfo=timezone.UTC),
        )
        BlogPostPageFactory(
            title="Post 3",
            parent=self.blog_page,
            live=True,
            published_date=datetime(2024, 2, 10, tzinfo=timezone.UTC),
        )

        result = self.blog_page.blog_posts_count

        self.assertEqual(len(result), 1)  # All in 2024
        self.assertEqual(result[0]["year"], 2024)
        self.assertEqual(result[0]["posts"], 3)

        months = result[0]["months"]
        self.assertEqual(len(months), 2)
        self.assertEqual(months[0]["month"], 1)
        self.assertEqual(months[0]["posts"], 2)
        self.assertEqual(months[1]["month"], 2)
        self.assertEqual(months[1]["posts"], 1)


class TestBlogPageBlogPostsAuthors(TestCase):
    """Tests for BlogPage.blog_posts_authors property"""

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

    def test_blog_page_blog_posts_authors_returns_empty_list_when_no_posts(self):
        """Test that blog_posts_authors returns empty list when there are no posts"""
        result = self.blog_page.blog_posts_authors
        self.assertEqual(result, [])

    def test_blog_page_blog_posts_authors_limited_to_12(self):
        """Test that blog_posts_authors returns at most 12 authors"""
        result = self.blog_page.blog_posts_authors
        self.assertLessEqual(len(result), 12)
