from datetime import date

from django.test import TestCase
from django.utils import timezone

from etna.home.factories import HomePageFactory

from ..factories import EventPageFactory, WhatsOnPageFactory
from ..models import AudienceType, EventAudienceType, EventSession, EventType


class TestWhatsOnPageEventFiltering(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home_page = HomePageFactory()

        cls.whats_on_page = WhatsOnPageFactory(title="What's On", parent=cls.home_page)

        cls.tour_event_type = EventType(
            name="Tour",
            slug="tour",
        )
        cls.tour_event_type.save()

        cls.talk_event_type = EventType(
            name="Talk",
            slug="talk",
        )
        cls.talk_event_type.save()

        cls.family_audience_type = AudienceType(
            name="Families",
            slug="families",
        )
        cls.family_audience_type.save()

        cls.event_audience_type = EventAudienceType(
            page=cls.whats_on_page,
            audience_type=cls.family_audience_type,
        )
        cls.event_audience_type.save()

        cls.event_page1 = EventPageFactory(
            title="Event page 1",
            parent=cls.whats_on_page,
            event_type=cls.talk_event_type,
            venue_type="online",
            start_date=timezone.datetime(2023, 10, 17),
            sessions=[
                EventSession(
                    page=cls.whats_on_page,
                    start=timezone.datetime(2023, 10, 15),
                    end=timezone.datetime(2023, 10, 16),
                )
            ],
        )

        cls.event_page2 = EventPageFactory(
            title="Event page 2",
            parent=cls.whats_on_page,
            event_type=cls.talk_event_type,
            event_audience_types=[cls.event_audience_type],
            venue_type="online",
            start_date=timezone.datetime(2023, 10, 17),
            sessions=[
                EventSession(
                    page=cls.whats_on_page,
                    start=timezone.datetime(2023, 10, 17),
                    end=timezone.datetime(2023, 10, 18),
                )
            ],
        )

        cls.event_page3 = EventPageFactory(
            title="Event page 3",
            parent=cls.whats_on_page,
            event_type=cls.tour_event_type,
            venue_type="in_person",
            start_date=timezone.datetime(2023, 10, 20),
            sessions=[
                EventSession(
                    page=cls.whats_on_page,
                    start=timezone.datetime(2023, 10, 20),
                    end=timezone.datetime(2023, 10, 21),
                )
            ],
        )

    def test_get_event_pages(self):
        self.assertQuerySetEqual(
            self.whats_on_page.events,
            [self.event_page1, self.event_page2, self.event_page3],
        )

    def assert_filtered_event_pages_equal(self, filter_params, expected_result):
        self.assertQuerySetEqual(
            self.whats_on_page.filter_form_data(filter_params), expected_result
        )

    def test_filtered_event_pages(self):
        test_cases = (
            ({}, [self.event_page1, self.event_page2, self.event_page3]),
            ({"is_online_event": True}, [self.event_page1, self.event_page2]),
            (
                {"event_type": self.talk_event_type},
                [self.event_page1, self.event_page2],
            ),
            ({"event_type": self.tour_event_type}, [self.event_page3]),
            ({"family_friendly": True}, [self.event_page2]),
            ({"date": date(2023, 10, 20)}, [self.event_page3]),
        )

        for filter_params, expected in test_cases:
            with self.subTest(filter_params=filter_params, expected=expected):
                self.assert_filtered_event_pages_equal(filter_params, expected)
