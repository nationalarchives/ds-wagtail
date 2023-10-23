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


class TestWhatsOnPageEventFiltering(TestCase):
    @classmethod
    def setUpTestData(self):
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
        self.assertQuerySetEqual(
            self.whats_on_page.events,
            [self.event_page1, self.event_page2, self.event_page3],
        )

    def assert_filtered_event_pages_equal(
            self, filter_params, expected_result
        ):
            self.assertQuerySetEqual(
                self.whats_on_page.filter_form_data(filter_params), expected_result
            )

    def test_filtered_event_pages(self):
        test_cases = (
            ({}, [self.event_page1, self.event_page2, self.event_page3]),
            ({"is_online_event": True}, [self.event_page1, self.event_page2]),
            ({"event_type": self.talk_event_type}, [self.event_page1, self.event_page2]),
            ({"event_type": self.tour_event_type}, [self.event_page3]),
            ({"family_friendly": True}, [self.event_page2]),
            ({"date": date(2023, 10, 20)}, [self.event_page3]),
        )

        for test in test_cases:
            self.assert_filtered_event_pages_equal(test[0], test[1])
