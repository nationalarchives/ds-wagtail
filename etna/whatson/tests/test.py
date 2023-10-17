from django.test import TestCase

from wagtail.models import Site

from ..models import WhatsOnPage, EventPage

from datetime import datetime, timedelta


class TestArticleIndexPage(TestCase):
    def setUp(self):
        self.root_page = Site.objects.get().root_page

        self.whats_on_page = WhatsOnPage(
            title="What's On Page",
            intro="test",
            teaser_text="test",
        )
        self.root_page.add_child(instance=self.whats_on_page)

        self.event_page1 = EventPage(
            title="Event page 1",
            intro="test",
            teaser_text="test",
            venue_type = "online",
            video_conference_info = "test",
            capacity = 2000,
            tickets_sold = 2000,
            min_price = 0,
            max_price = 0,
        )
        self.whats_on_page.add_child(instance=self.event_page1)

        self.event_page2 = EventPage(
            title="Event page 2",
            intro="test",
            teaser_text="test",
            venue_type = "online",
            video_conference_info = "test",
            capacity = 2000,
            tickets_sold = 1900,
            min_price = 0,
            max_price = 15,
        )
        self.whats_on_page.add_child(instance=self.event_page2)

        self.event_page3 = EventPage(
            title="Event page 3",
            intro="test",
            teaser_text="test",
            venue_type = "online",
            video_conference_info = "test",
            capacity = 2000,
            tickets_sold = 1000,
            min_price = 15,
            max_price = 30,
        )
        self.whats_on_page.add_child(instance=self.event_page3)

    def test_get_event_pages(self):
        self.assertEqual(
            list(self.whats_on_page.events),
            [self.event_page1, self.event_page2, self.event_page3]
        )

    def test_tickets_remaining(self):
        self.assertEqual(self.event_page1.tickets_remaining, 0)
        self.assertEqual(self.event_page2.tickets_remaining, 100)
        self.assertEqual(self.event_page3.tickets_remaining, 1000)

    def test_price_range(self):
        self.assertEqual(self.event_page1.price_range, "Free")
        self.assertEqual(self.event_page2.price_range, "Free - 15")
        self.assertEqual(self.event_page3.price_range, "15 - 30")
