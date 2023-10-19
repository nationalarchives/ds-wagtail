from datetime import date

from django.test import TestCase
from django.utils import timezone

from wagtail.models import Site

from etna.images.models import CustomImage

from ..models import (
    AudienceType,
    EventAudienceType,
    EventPage,
    EventSession,
    EventType,
    WhatsOnPage,
)


class TestEvents(TestCase):
    def setUp(self):
        self.root_page = Site.objects.get().root_page

        self.whats_on_page = WhatsOnPage(
            title="What's On Page",
            intro="test",
            teaser_text="test",
        )
        self.root_page.add_child(instance=self.whats_on_page)

        self.tour_event_type = EventType(
            name="Tour",
            slug="tour",
        )
        self.root_page.add_child(instance=self.tour_event_type)

        self.talk_event_type = EventType(
            name="Talk",
            slug="talk",
        )
        self.root_page.add_child(instance=self.talk_event_type)

        self.family_audience_type = AudienceType(
            name="Families",
            slug="families",
        )
        self.root_page.add_child(instance=self.family_audience_type)

        self.event_audience_type = EventAudienceType(
            page=self.root_page,
            audience_type=self.family_audience_type,
        )
        self.root_page.add_child(instance=self.event_audience_type)

        self.custom_image = CustomImage(
            width=100,
            height=100,
        )
        self.root_page.add_child(instance=self.custom_image)

        self.event_page1 = EventPage(
            title="Event page 1",
            intro="test",
            teaser_text="test",
            venue_type="online",
            video_conference_info="test",
            short_title="test",
            event_type=self.talk_event_type,
            lead_image=self.custom_image,
            start_date=timezone.datetime(2023, 10, 17),
            sessions=[
                EventSession(
                    page=self.root_page,
                    start=timezone.datetime(2023, 10, 15),
                    end=timezone.datetime(2023, 10, 16),
                )
            ],
        )
        self.whats_on_page.add_child(instance=self.event_page1)

        self.event_page2 = EventPage(
            title="Event page 2",
            intro="test",
            teaser_text="test",
            venue_type="online",
            video_conference_info="test",
            short_title="test",
            event_type=self.talk_event_type,
            lead_image=self.custom_image,
            event_audience_types=[self.event_audience_type],
            sessions=[
                EventSession(
                    page=self.root_page,
                    start=timezone.datetime(2023, 10, 17),
                    end=timezone.datetime(2023, 10, 18),
                )
            ],
        )
        self.whats_on_page.add_child(instance=self.event_page2)

        self.event_page3 = EventPage(
            title="Event page 3",
            intro="test",
            teaser_text="test",
            venue_type="in_person",
            venue_address="test",
            venue_space_name="test",
            short_title="test",
            event_type=self.tour_event_type,
            lead_image=self.custom_image,
            sessions=[
                EventSession(
                    page=self.root_page,
                    start=timezone.datetime(2023, 10, 20),
                    end=timezone.datetime(2023, 10, 21),
                )
            ],
        )
        self.whats_on_page.add_child(instance=self.event_page3)

    def test_get_event_pages(self):
        self.assertEqual(
            list(self.whats_on_page.events),
            [self.event_page1, self.event_page2, self.event_page3],
        )

    def test_filtered_event_pages(self):
        def filter_check(
            date, event_type, is_online_event, family_friendly, expected_result
        ):
            filter_data = {
                "date": date,
                "event_type": event_type,
                "is_online_event": is_online_event,
                "family_friendly": family_friendly,
            }
            self.assertEqual(
                list(self.whats_on_page.filter_form_data(filter_data)), expected_result
            )

        test_cases = [
            [
                None,
                None,
                None,
                None,
                [self.event_page1, self.event_page2, self.event_page3],
            ],
            [None, None, True, None, [self.event_page1, self.event_page2]],
            [
                None,
                self.talk_event_type,
                None,
                None,
                [self.event_page1, self.event_page2],
            ],
            [None, self.tour_event_type, None, None, [self.event_page3]],
            [None, None, None, True, [self.event_page2]],
            [date(2023, 10, 20), None, None, None, [self.event_page3]],
        ]

        for test in test_cases:
            filter_check(test[0], test[1], test[2], test[3], test[4])
