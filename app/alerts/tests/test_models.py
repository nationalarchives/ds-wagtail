from app.alerts.models import Alert
from app.generic_pages.factories import GeneralPageFactory
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase


class AlertMixinCascadeTests(WagtailPageTestCase):
    """
    Tests for alert cascade behavior.

    Tests the cascade logic implemented in BaseAlertMixin.get_active_alert(),
    which is shared by both AlertMixin and ThemedAlertMixin.
    Uses AlertMixin with GeneralPage as the test implementation.
    """

    def setUp(self):
        self.root_page = Site.objects.get(is_default_site=True).root_page

        # Create parent page
        self.parent_page = GeneralPageFactory(
            title="Parent Page", parent=self.root_page
        )

        # Create child page
        self.child_page = GeneralPageFactory(
            title="Child Page", parent=self.parent_page
        )

        # Create grandchild page
        self.grandchild_page = GeneralPageFactory(
            title="Grandchild Page", parent=self.child_page
        )

    def test_no_alert_set_returns_none(self):
        """When no alert is set, global_alert should return None"""
        self.assertIsNone(self.child_page.global_alert)

    def test_page_with_active_alert_displays_alert(self):
        """Page with an active alert should display it"""
        alert = Alert.objects.create(
            name="Test Alert",
            title="Important",
            message="This is a test",
            active=True,
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )
        self.child_page.alert = alert
        self.child_page.save()

        self.assertEqual(self.child_page.global_alert, alert)

    def test_page_with_inactive_alert_returns_none(self):
        """Page with an inactive alert should return None"""
        alert = Alert.objects.create(
            name="Test Alert",
            title="Important",
            message="This is a test",
            active=False,
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )
        self.child_page.alert = alert
        self.child_page.save()

        self.assertIsNone(self.child_page.global_alert)

    def test_child_and_parent_different_alerts_no_cascade(self):
        """Child and parent with different alerts (no cascade) should show their own alerts"""
        parent_alert = Alert.objects.create(
            name="Parent Alert",
            title="Parent",
            message="Parent message",
            active=True,
            cascade=False,
            alert_level=Alert.AlertLevelChoices.LOW,
        )
        child_alert = Alert.objects.create(
            name="Child Alert",
            title="Child",
            message="Child message",
            active=True,
            cascade=False,
            alert_level=Alert.AlertLevelChoices.HIGH,
        )

        self.parent_page.alert = parent_alert
        self.parent_page.save()

        self.child_page.alert = child_alert
        self.child_page.save()

        # Parent should show parent alert
        self.assertEqual(self.parent_page.global_alert, parent_alert)
        # Child should show child alert
        self.assertEqual(self.child_page.global_alert, child_alert)

    def test_parent_cascade_overrides_child_active_alert(self):
        """Parent alert with cascade should override child's own active alert"""
        parent_alert = Alert.objects.create(
            name="Parent Alert",
            title="Parent",
            message="Parent message",
            active=True,
            cascade=True,
            alert_level=Alert.AlertLevelChoices.HIGH,
        )
        child_alert = Alert.objects.create(
            name="Child Alert",
            title="Child",
            message="Child message",
            active=True,
            cascade=False,
            alert_level=Alert.AlertLevelChoices.LOW,
        )

        self.parent_page.alert = parent_alert
        self.parent_page.save()

        self.child_page.alert = child_alert
        self.child_page.save()

        # Child should display parent's cascading alert
        self.assertEqual(self.child_page.global_alert, parent_alert)

    def test_parent_cascade_with_inactive_child_alert(self):
        """Parent cascade should work even when child has inactive alert"""
        parent_alert = Alert.objects.create(
            name="Parent Alert",
            title="Parent",
            message="Parent message",
            active=True,
            cascade=True,
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )
        child_alert = Alert.objects.create(
            name="Child Alert",
            title="Child",
            message="Child message",
            active=False,
            cascade=False,
            alert_level=Alert.AlertLevelChoices.LOW,
        )

        self.parent_page.alert = parent_alert
        self.parent_page.save()

        self.child_page.alert = child_alert
        self.child_page.save()

        # Child should display parent's cascading alert
        self.assertEqual(self.child_page.global_alert, parent_alert)

    def test_grandchild_inherits_from_grandparent_cascade(self):
        """Cascade should work through multiple levels of hierarchy"""
        grandparent_alert = Alert.objects.create(
            name="Grandparent Alert",
            title="Grandparent",
            message="Grandparent message",
            active=True,
            cascade=True,
            alert_level=Alert.AlertLevelChoices.HIGH,
        )

        self.parent_page.alert = grandparent_alert
        self.parent_page.save()

        # Grandchild should inherit cascading alert
        self.assertEqual(self.grandchild_page.global_alert, grandparent_alert)

    def test_inactive_parent_cascade_does_not_override_child(self):
        """Inactive parent alert with cascade should not override child's active alert"""
        parent_alert = Alert.objects.create(
            name="Parent Alert",
            title="Parent",
            message="Parent message",
            active=False,
            cascade=True,
            alert_level=Alert.AlertLevelChoices.HIGH,
        )
        child_alert = Alert.objects.create(
            name="Child Alert",
            title="Child",
            message="Child message",
            active=True,
            cascade=False,
            alert_level=Alert.AlertLevelChoices.LOW,
        )

        self.parent_page.alert = parent_alert
        self.parent_page.save()

        self.child_page.alert = child_alert
        self.child_page.save()

        # Child should display its own alert since parent is inactive
        self.assertEqual(self.child_page.global_alert, child_alert)
