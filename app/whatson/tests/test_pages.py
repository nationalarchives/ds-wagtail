# import urllib

# from datetime import date, datetime

# from django.test import RequestFactory, TestCase
# from django.utils import timezone

# from app.home.factories import HomePageFactory

# from ..factories import EventPageFactory, WhatsOnPageFactory
# from ..models import AudienceType, EventAudienceType, EventSession, EventType


# class TestWhatsOnPageEventFiltering(TestCase):
#     def setUp(self):
#         super().setUp()
#         self.factory = RequestFactory()

#     @classmethod
#     def setUpTestData(cls):
#         cls.home_page = HomePageFactory()

#         cls.whats_on_page = WhatsOnPageFactory(title="What's On", parent=cls.home_page)

#         cls.tour_event_type = EventType(
#             name="Tour",
#             slug="tour",
#         )
#         cls.tour_event_type.save()

#         cls.talk_event_type = EventType(
#             name="Talk",
#             slug="talk",
#         )
#         cls.talk_event_type.save()

#         cls.family_audience_type = AudienceType(
#             name="Families",
#             slug="families",
#         )
#         cls.family_audience_type.save()

#         cls.event_audience_type = EventAudienceType(
#             page=cls.whats_on_page,
#             audience_type=cls.family_audience_type,
#         )
#         cls.event_audience_type.save()

#         cls.featured_event = EventPageFactory(
#             title="Event page 1",
#             parent=cls.whats_on_page,
#             event_type=cls.talk_event_type,
#             venue_type="online",
#             min_price=0,
#             max_price=0,
#             start_date=timezone.make_aware(datetime(2023, 10, 17)),
#             sessions=[
#                 EventSession(
#                     page=cls.whats_on_page,
#                     start=timezone.make_aware(datetime(2023, 10, 15)),
#                     end=timezone.make_aware(datetime(2023, 10, 16)),
#                 )
#             ],
#         )
#         cls.whats_on_page.featured_event = cls.featured_event

#         cls.event_page_2 = EventPageFactory(
#             title="Event page 2",
#             parent=cls.whats_on_page,
#             event_type=cls.talk_event_type,
#             event_audience_types=[cls.event_audience_type],
#             venue_type="online",
#             min_price=0,
#             max_price=15,
#             start_date=timezone.make_aware(datetime(2023, 10, 17)),
#             sessions=[
#                 EventSession(
#                     page=cls.whats_on_page,
#                     start=timezone.make_aware(datetime(2023, 10, 17)),
#                     end=timezone.make_aware(datetime(2023, 10, 18)),
#                 )
#             ],
#         )

#         cls.event_page_3 = EventPageFactory(
#             title="Event page 3",
#             parent=cls.whats_on_page,
#             event_type=cls.tour_event_type,
#             venue_type="in_person",
#             min_price=15,
#             max_price=30,
#             start_date=timezone.make_aware(datetime(2023, 10, 20)),
#             sessions=[
#                 EventSession(
#                     page=cls.whats_on_page,
#                     start=timezone.make_aware(datetime(2023, 10, 20)),
#                     end=timezone.make_aware(datetime(2023, 10, 21)),
#                 )
#             ],
#         )

#         cls.event_page_4 = EventPageFactory(
#             title="Event page 4",
#             parent=cls.whats_on_page,
#             event_type=cls.tour_event_type,
#             venue_type="in_person",
#             min_price=15,
#             max_price=30,
#             start_date=timezone.make_aware(datetime(2023, 10, 20)),
#             sessions=[
#                 EventSession(
#                     page=cls.whats_on_page,
#                     start=timezone.make_aware(datetime(2023, 10, 20, 10, 30)),
#                     end=timezone.make_aware(datetime(2023, 10, 20, 20, 30)),
#                 )
#             ],
#         )

#         cls.event_page_5 = EventPageFactory(
#             title="Event page 5",
#             parent=cls.whats_on_page,
#             event_type=cls.tour_event_type,
#             venue_type="in_person",
#             min_price=15,
#             max_price=30,
#             start_date=timezone.make_aware(datetime(2023, 10, 22)),
#             sessions=[
#                 EventSession(
#                     page=cls.whats_on_page,
#                     start=timezone.make_aware(datetime(2023, 10, 22, 10, 30)),
#                     end=timezone.make_aware(datetime(2023, 10, 22, 10, 30)),
#                 )
#             ],
#         )

#         cls.event_page_6 = EventPageFactory(
#             title="Event page 6",
#             parent=cls.whats_on_page,
#             event_type=cls.tour_event_type,
#             venue_type="in_person",
#             min_price=15,
#             max_price=30,
#             start_date=timezone.make_aware(datetime(2023, 10, 22)),
#             sessions=[
#                 EventSession(
#                     page=cls.whats_on_page,
#                     start=timezone.make_aware(datetime(2023, 10, 22, 10, 30)),
#                     end=timezone.make_aware(datetime(2023, 10, 22, 11, 30)),
#                 ),
#                 EventSession(
#                     page=cls.whats_on_page,
#                     start=timezone.make_aware(datetime(2023, 10, 22, 11, 30)),
#                     end=timezone.make_aware(datetime(2023, 10, 22, 12, 30)),
#                 ),
#             ],
#         )
#     def assert_filtered_event_pages_equal(self, filter_params, expected_result):
#         events = self.whats_on_page.get_events_queryset()
#         self.assertQuerySetEqual(
#             self.whats_on_page.filter_events(events, filter_params), expected_result
#         )

#     def test_filtered_event_pages(self):
#         test_cases = (
#             (
#                 {},
#                 [
#                     self.featured_event,
#                     self.event_page_2,
#                     self.event_page_3,
#                     self.event_page_4,
#                     self.event_page_5,
#                     self.event_page_6,
#                 ],
#             ),
#             ({"is_online_event": True}, [self.featured_event, self.event_page_2]),
#             (
#                 {"event_type": self.talk_event_type},
#                 [self.featured_event, self.event_page_2],
#             ),
#             (
#                 {"event_type": self.tour_event_type},
#                 [
#                     self.event_page_3,
#                     self.event_page_4,
#                     self.event_page_5,
#                     self.event_page_6,
#                 ],
#             ),
#             ({"family_friendly": True}, [self.event_page_2]),
#             ({"date": date(2023, 10, 20)}, [self.event_page_3, self.event_page_4]),
#         )

#         for filter_params, expected in test_cases:
#             with self.subTest(filter_params=filter_params, expected=expected):
#                 self.assert_filtered_event_pages_equal(filter_params, expected)
