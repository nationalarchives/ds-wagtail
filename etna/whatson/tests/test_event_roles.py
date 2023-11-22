from django.core.exceptions import ValidationError
from django.test import TestCase

from wagtail_factories import ImageFactory

from etna.authors.factories import AuthorPageFactory
from etna.whatson.factories import (
    EventHostFactory,
    EventSpeakerFactory,
)


class TestEventRoles(TestCase):
    def test_clean_method_raises(self):
        params = [
            # EventHost tests
            (EventHostFactory.build(person_page=None), "Please select a page"),
            (
                EventHostFactory.build(
                    person_page=AuthorPageFactory.build(), name="Name"
                ),
                "Either select a page",
            ),
            (
                EventHostFactory.build(
                    person_page=AuthorPageFactory.build(), description="Description"
                ),
                "Either select a page",
            ),
            (
                EventHostFactory.build(
                    person_page=AuthorPageFactory.build(), image=ImageFactory.build()
                ),
                "Either select a page",
            ),
            # EventSpeaker tests
            (EventSpeakerFactory.build(person_page=None), "Please select a page"),
            (
                EventSpeakerFactory.build(
                    person_page=AuthorPageFactory.build(), name="Name"
                ),
                "Either select a page",
            ),
            (
                EventSpeakerFactory.build(
                    person_page=AuthorPageFactory.build(), description="Description"
                ),
                "Either select a page",
            ),
            (
                EventSpeakerFactory.build(
                    person_page=AuthorPageFactory.build(), image=ImageFactory.build()
                ),
                "Either select a page",
            ),
        ]
        for instance, pattern in params:
            with self.subTest(instance=instance, expected_message=pattern):
                with self.assertRaisesRegex(ValidationError, pattern):
                    instance.clean()
