from django.test import TestCase

from wagtail.models import Site

from ..alerts.models import Alert
from ..alerts.templatetags import alert_tags
from ..home.models import HomePage


def rich_text_msg(level):
    msg = (
        "<p>This is a <b>{level}</b> severity alert. "
        "Here is some extra text to show what a detailed alert would look like. "
        '<a href="/">Find out more</a>.</p>'
    )
    return msg.format(level=level)


class AlertTestCase(TestCase):
    def setUp(self):
        # Create inactive, non-cascading alerts
        self.alert_low = Alert.objects.create(
            title="Notice", message=rich_text_msg("low"), alert_level="low"
        )
        self.alert_medium = Alert.objects.create(
            title="Alert", message=rich_text_msg("medium"), alert_level="medium"
        )
        self.alert_high = Alert.objects.create(
            title="Warning", message=rich_text_msg("high"), alert_level="high"
        )
        # Create page heirarchy
        self.root = Site.objects.get().root_page
        self.home_page = HomePage(
            title="Home",
            live=True,
            intro="test",
            teaser_text="test",
            alert=self.alert_high,
        )
        self.root.add_child(instance=self.home_page)

    def test_current_page_alerts(self):
        # Ensure cascade is off
        self.alert_high.cascade = False
        self.alert_medium.cascade = False
        self.alert_low.cascade = False

        # Test home page - currently asigned high alert
        # .. inactive
        self.alert_high.active = False
        alerts = alert_tags.alerts(self.home_page)["alerts"]
        self.assertEqual(len(alerts), 0)
        # .. active
        self.alert_high.active = True
        alerts = alert_tags.alerts(self.home_page)["alerts"]
        self.assertEqual(len(alerts), 1)

    def test_cascading_page_alerts(self):
        # Ensure cascade is off to begin
        self.alert_high.cascade = False
        self.alert_medium.cascade = False
        self.alert_low.cascade = False
        # Deactivate all alerts
        self.alert_high.active = False
        self.alert_medium.active = False
        self.alert_low.active = False

        # All pages should have 0 alerts
        alerts = alert_tags.alerts(self.home_page)["alerts"]
        self.assertEqual(len(alerts), 0)

        # Activate all alerts
        self.alert_high.active = True
        self.alert_medium.active = True
        self.alert_low.active = True

        # All pages should have 1 alert (none inherited)
        alerts = alert_tags.alerts(self.home_page)["alerts"]
        self.assertEqual(len(alerts), 1)

        # Enable cascade
        # For some reason tests will fail without a save() on each alert.
        # Although it is not necessary for the other boolean field (active). ???
        self.alert_high.cascade = True
        self.alert_high.save()
        self.alert_medium.cascade = True
        self.alert_medium.save()
        self.alert_low.cascade = True
        self.alert_low.save()

        # Each page should inherit an extra alert from its parent
        alerts = alert_tags.alerts(self.home_page)["alerts"]
        self.assertEqual(len(alerts), 1)
