import factory
from django.utils import timezone
from wagtail_factories import ImageFactory, PageFactory

from app.people.models import PeopleIndexPage, PersonPage


class PeopleIndexPageFactory(PageFactory):
    teaser_text = "Teaser text"
    teaser_image = factory.SubFactory(ImageFactory)

    class Meta:
        model = PeopleIndexPage


class PersonPageFactory(PageFactory):
    image = factory.SubFactory(ImageFactory)
    teaser_text = "Teaser text"
    teaser_image = factory.SubFactory(ImageFactory)

    class Meta:
        model = PersonPage

    @factory.post_generation
    def set_publish_dates(obj, create, extracted, **kwargs):
        if obj.live and obj.first_published_at is None:
            obj.first_published_at = (
                obj.last_published_at
                or obj.latest_revision_created_at
                or timezone.now()
            )
        if obj.live and obj.last_published_at is None:
            obj.last_published_at = (
                obj.latest_revision_created_at or obj.first_published_at
            )
