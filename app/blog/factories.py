import factory
from django.utils import timezone
from wagtail_factories import ImageFactory

from app.blog.models import BlogFeedsPage, BlogIndexPage, BlogPage, BlogPostPage
from app.core.factories import BasePageFactory


class BlogIndexPageFactory(BasePageFactory):
    """Factory for creating BlogIndexPage instances"""

    class Meta:
        model = BlogIndexPage


class BlogPageFactory(BasePageFactory):
    """Factory for creating BlogPage instances"""

    hero_image = factory.SubFactory(ImageFactory)
    hero_image_caption = "<p>Hero image caption</p>"
    custom_type_label = ""

    class Meta:
        model = BlogPage


class BlogPostPageFactory(BasePageFactory):
    """Factory for creating BlogPostPage instances"""

    hero_image = factory.SubFactory(ImageFactory)
    hero_image_caption = "<p>Hero image caption</p>"
    published_date = factory.LazyFunction(lambda: timezone.now())

    class Meta:
        model = BlogPostPage
        skip_postgeneration_save = True

    @factory.post_generation
    def set_publish_dates(obj, create, extracted, **kwargs):
        save = False

        if obj.live and obj.first_published_at is None:
            obj.first_published_at = (
                obj.last_published_at
                or obj.latest_revision_created_at
                or timezone.now()
            )
            save = True

        if obj.live and obj.last_published_at is None:
            obj.last_published_at = (
                obj.latest_revision_created_at or obj.first_published_at
            )
            save = True

        if create and save:
            obj.save()


class BlogFeedsPageFactory(BasePageFactory):
    """Factory for creating BlogFeedsPage instances"""

    class Meta:
        model = BlogFeedsPage
