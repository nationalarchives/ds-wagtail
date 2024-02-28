import urllib

from datetime import date, datetime

from django.test import RequestFactory, TestCase
from django.utils import timezone

from etna.home.factories import HomePageFactory

from ..factories import EventPageFactory, WhatsOnPageFactory
from ..models import AudienceType, EventAudienceType, EventSession, EventType


class TestWhatsOnPageEventFiltering(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        cls.home_page = HomePageFactory()

        cls.whats_on_page = WhatsOnPageFactory(
            title="What's On", parent=cls.home_page
        )

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

        cls.featured_event = EventPageFactory(
            title="Event page 1",
            parent=cls.whats_on_page,
            event_type=cls.talk_event_type,
            venue_type="online",
            min_price=0,
            max_price=0,
            start_date=timezone.make_aware(datetime(2023, 10, 17)),
            sessions=[
                EventSession(
                    page=cls.whats_on_page,
                    start=timezone.make_aware(datetime(2023, 10, 15)),
                    end=timezone.make_aware(datetime(2023, 10, 16)),
                )
            ],
        )
        cls.whats_on_page.featured_event = cls.featured_event

        cls.event_page_2 = EventPageFactory(
            title="Event page 2",
            parent=cls.whats_on_page,
            event_type=cls.talk_event_type,
            event_audience_types=[cls.event_audience_type],
            venue_type="online",
            min_price=0,
            max_price=15,
            start_date=timezone.make_aware(datetime(2023, 10, 17)),
            sessions=[
                EventSession(
                    page=cls.whats_on_page,
                    start=timezone.make_aware(datetime(2023, 10, 17)),
                    end=timezone.make_aware(datetime(2023, 10, 18)),
                )
            ],
        )

        cls.event_page_3 = EventPageFactory(
            title="Event page 3",
            parent=cls.whats_on_page,
            event_type=cls.tour_event_type,
            venue_type="in_person",
            min_price=15,
            max_price=30,
            start_date=timezone.make_aware(datetime(2023, 10, 20)),
            sessions=[
                EventSession(
                    page=cls.whats_on_page,
                    start=timezone.make_aware(datetime(2023, 10, 20)),
                    end=timezone.make_aware(datetime(2023, 10, 21)),
                )
            ],
        )

        cls.event_page_4 = EventPageFactory(
            title="Event page 4",
            parent=cls.whats_on_page,
            event_type=cls.tour_event_type,
            venue_type="in_person",
            min_price=15,
            max_price=30,
            start_date=timezone.make_aware(datetime(2023, 10, 20)),
            sessions=[
                EventSession(
                    page=cls.whats_on_page,
                    start=timezone.make_aware(datetime(2023, 10, 20, 10, 30)),
                    end=timezone.make_aware(datetime(2023, 10, 20, 20, 30)),
                )
            ],
        )

        cls.event_page_5 = EventPageFactory(
            title="Event page 5",
            parent=cls.whats_on_page,
            event_type=cls.tour_event_type,
            venue_type="in_person",
            min_price=15,
            max_price=30,
            start_date=timezone.make_aware(datetime(2023, 10, 22)),
            sessions=[
                EventSession(
                    page=cls.whats_on_page,
                    start=timezone.make_aware(datetime(2023, 10, 22, 10, 30)),
                    end=timezone.make_aware(datetime(2023, 10, 22, 10, 30)),
                )
            ],
        )

        cls.event_page_6 = EventPageFactory(
            title="Event page 6",
            parent=cls.whats_on_page,
            event_type=cls.tour_event_type,
            venue_type="in_person",
            min_price=15,
            max_price=30,
            start_date=timezone.make_aware(datetime(2023, 10, 22)),
            sessions=[
                EventSession(
                    page=cls.whats_on_page,
                    start=timezone.make_aware(datetime(2023, 10, 22, 10, 30)),
                    end=timezone.make_aware(datetime(2023, 10, 22, 11, 30)),
                ),
                EventSession(
                    page=cls.whats_on_page,
                    start=timezone.make_aware(datetime(2023, 10, 22, 11, 30)),
                    end=timezone.make_aware(datetime(2023, 10, 22, 12, 30)),
                ),
            ],
        )

    def test_get_event_pages(self):
        self.assertQuerySetEqual(
            self.whats_on_page.get_events_queryset(),
            [
                self.featured_event,
                self.event_page_2,
                self.event_page_3,
                self.event_page_4,
                self.event_page_5,
                self.event_page_6,
            ],
        )

    def assert_filtered_event_pages_equal(self, filter_params, expected_result):
        events = self.whats_on_page.get_events_queryset()
        self.assertQuerySetEqual(
            self.whats_on_page.filter_events(events, filter_params),
            expected_result,
        )

    def test_filtered_event_pages(self):
        test_cases = (
            (
                {},
                [
                    self.featured_event,
                    self.event_page_2,
                    self.event_page_3,
                    self.event_page_4,
                    self.event_page_5,
                    self.event_page_6,
                ],
            ),
            (
                {"is_online_event": True},
                [self.featured_event, self.event_page_2],
            ),
            (
                {"event_type": self.talk_event_type},
                [self.featured_event, self.event_page_2],
            ),
            (
                {"event_type": self.tour_event_type},
                [
                    self.event_page_3,
                    self.event_page_4,
                    self.event_page_5,
                    self.event_page_6,
                ],
            ),
            ({"family_friendly": True}, [self.event_page_2]),
            (
                {"date": date(2023, 10, 20)},
                [self.event_page_3, self.event_page_4],
            ),
        )

        for filter_params, expected in test_cases:
            with self.subTest(filter_params=filter_params, expected=expected):
                self.assert_filtered_event_pages_equal(filter_params, expected)

    def test_price_range(self):
        test_cases = (
            (self.featured_event.price_range, "Free"),
            (self.event_page_2.price_range, "Free - 15"),
            (self.event_page_3.price_range, "15 - 30"),
        )

        for test_value, expected in test_cases:
            with self.subTest(test_value=test_value, expected=expected):
                self.assertEqual(test_value, expected)

    def test_date_time_range(self):
        test_cases = (
            (
                self.event_page_3.date_time_range,
                "20 October 2023 to 21 October 2023",
            ),
            # note this expects an en dash
            (
                self.event_page_4.date_time_range,
                "Friday 20 October 2023, 10:30–20:30",
            ),
            (
                self.event_page_5.date_time_range,
                "Sunday 22 October 2023, 10:30",
            ),
            (self.event_page_6.date_time_range, "Sunday 22 October 2023"),
        )

        for test_value, expected in test_cases:
            with self.subTest(test_value=test_value, expected=expected):
                self.assertEqual(test_value, expected)

    def test_remove_filter_urls(self):
        """
        The URL we generate to remove a filter from the listing should not include that field
        """
        query_dict = {
            "date": "2023-10-03",
            "event_type": self.talk_event_type.id,
            "is_online_event": "on",
            "family_friendly": "on",
        }
        query_string = urllib.parse.urlencode(query_dict)
        request_url = f"/?{query_string}"
        request = RequestFactory().get(request_url)

        for field_name in query_dict.keys():
            with self.subTest(field_name=field_name):
                url_parts = urllib.parse.urlparse(
                    self.whats_on_page.build_unset_filter_url(
                        request, field_name
                    )
                )
                updated_query_dict = urllib.parse.parse_qs(url_parts.query)
                self.assertNotIn(field_name, updated_query_dict)

    def test_should_not_show_featured_event(self):
        self.assertEqual(self.featured_event.event_type, self.talk_event_type)
        request = self.factory.get(
            self.whats_on_page.url, {"event_type": self.tour_event_type.pk}
        )

        context = self.whats_on_page.get_context(request)
        # We filtered for events with type "tour", featured event is type
        # "talk", so should not be displayed
        self.assertFalse(context["show_featured_event"])
        self.assertNotIn(self.featured_event, context["events"])

    def test_should_show_featured_event(self):
        self.assertEqual(self.featured_event.event_type, self.talk_event_type)
        request = self.factory.get(
            self.whats_on_page.url, {"event_type": self.talk_event_type.pk}
        )

        context = self.whats_on_page.get_context(request)
        self.assertTrue(context["show_featured_event"])
        self.assertNotIn(self.featured_event, context["events"])

    def test_featured_event_not_in_main_listing(self):
        """
        Featured event should never be in the main events listing
        """
        request = self.factory.get(self.whats_on_page.url)
        context = self.whats_on_page.get_context(request)
        self.assertIn(
            self.featured_event, self.whats_on_page.get_events_queryset()
        )
        self.assertNotIn(self.featured_event, context["events"])
