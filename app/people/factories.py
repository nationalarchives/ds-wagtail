import factory
from app.people.models import PeopleIndexPage, PersonPage
from django.utils import timezone
from wagtail_factories import ImageFactory, PageFactory


class PeopleIndexPageFactory(PageFactory):
    teaser_text = "Teaser text"
    teaser_image = factory.SubFactory(ImageFactory)

    class Meta:
        model = PeopleIndexPage


class PersonPageFactory(PageFactory):
    teaser_text = "Teaser text"
    teaser_image = factory.SubFactory(ImageFactory)
    image = factory.SubFactory(ImageFactory)

    class Meta:
        model = PersonPage
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
