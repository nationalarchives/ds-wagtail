from app.alerts.factories import TestAlertPageFactory, TestThemedAlertPageFactory
from app.alerts.models import Alert, ThemedAlert
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase


class AlertTests(WagtailPageTestCase):
    """Tests for Alert model and AlertMixin"""

    def setUp(self):
        self.root_page = Site.objects.get(is_default_site=True).root_page

        # Create parent page
        self.parent_page = TestAlertPageFactory(
            title="Parent Page", parent=self.root_page
        )

        # Create child page
        self.child_page = TestAlertPageFactory(
            title="Child Page", parent=self.parent_page
        )

        # Create grandchild page
        self.grandchild_page = TestAlertPageFactory(
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

    def test_alert_levels(self):
        """Alert should correctly store and retrieve all alert levels"""
        for level in Alert.AlertLevelChoices:
            with self.subTest(level=level):
                alert = Alert.objects.create(
                    name=f"{level.label} Alert",
                    title=level.label,
                    message=f"{level.label} priority",
                    active=True,
                    alert_level=level,
                )
                self.assertEqual(alert.alert_level, level)

    def test_alert_level_default_is_low(self):
        """Alert level should default to 'low' if not specified"""
        alert = Alert.objects.create(
            name="Default Alert",
            title="Default",
            message="Default message",
            active=True,
        )
        self.assertEqual(alert.alert_level, Alert.AlertLevelChoices.LOW)

    def test_alert_str_method(self):
        """Alert __str__ should return the name"""
        alert = Alert.objects.create(
            name="Test Alert Name",
            title="Title",
            message="Message",
            active=True,
        )
        self.assertEqual(str(alert), "Test Alert Name")


class ThemedAlertTests(WagtailPageTestCase):
    """Tests for ThemedAlert model and ThemedAlertMixin"""

    def setUp(self):
        self.root_page = Site.objects.get(is_default_site=True).root_page

        # Create parent page
        self.parent_page = TestThemedAlertPageFactory(
            title="Parent Page", parent=self.root_page
        )

        # Create child page
        self.child_page = TestThemedAlertPageFactory(
            title="Child Page", parent=self.parent_page
        )

        # Create grandchild page
        self.grandchild_page = TestThemedAlertPageFactory(
            title="Grandchild Page", parent=self.child_page
        )

    def test_no_alert_set_returns_none(self):
        """When no alert is set, global_alert should return None"""
        self.assertIsNone(self.child_page.global_alert)

    def test_page_with_active_themed_alert_displays_alert(self):
        """Page with an active themed alert should display it"""
        alert = ThemedAlert.objects.create(
            name="Test Themed Alert",
            title="Important",
            message="This is a test",
            active=True,
            theme=ThemedAlert.AlertThemeChoices.YELLOW,
        )
        self.child_page.themed_alert = alert
        self.child_page.save()

        self.assertEqual(self.child_page.global_alert, alert)

    def test_page_with_inactive_themed_alert_returns_none(self):
        """Page with an inactive themed alert should return None"""
        alert = ThemedAlert.objects.create(
            name="Test Themed Alert",
            title="Important",
            message="This is a test",
            active=False,
            theme=ThemedAlert.AlertThemeChoices.RED,
        )
        self.child_page.themed_alert = alert
        self.child_page.save()

        self.assertIsNone(self.child_page.global_alert)

    def test_child_and_parent_different_alerts_no_cascade(self):
        """Child and parent with different themed alerts (no cascade) should show their own alerts"""
        parent_alert = ThemedAlert.objects.create(
            name="Parent Alert",
            title="Parent",
            message="Parent message",
            active=True,
            cascade=False,
            theme=ThemedAlert.AlertThemeChoices.GREEN,
        )
        child_alert = ThemedAlert.objects.create(
            name="Child Alert",
            title="Child",
            message="Child message",
            active=True,
            cascade=False,
            theme=ThemedAlert.AlertThemeChoices.RED,
        )

        self.parent_page.themed_alert = parent_alert
        self.parent_page.save()

        self.child_page.themed_alert = child_alert
        self.child_page.save()

        # Parent should show parent alert
        self.assertEqual(self.parent_page.global_alert, parent_alert)
        # Child should show child alert
        self.assertEqual(self.child_page.global_alert, child_alert)

    def test_parent_cascade_overrides_child_active_alert(self):
        """Parent themed alert with cascade should override child's own active alert"""
        parent_alert = ThemedAlert.objects.create(
            name="Parent Alert",
            title="Parent",
            message="Parent message",
            active=True,
            cascade=True,
            theme=ThemedAlert.AlertThemeChoices.RED,
        )
        child_alert = ThemedAlert.objects.create(
            name="Child Alert",
            title="Child",
            message="Child message",
            active=True,
            cascade=False,
            theme=ThemedAlert.AlertThemeChoices.GREEN,
        )

        self.parent_page.themed_alert = parent_alert
        self.parent_page.save()

        self.child_page.themed_alert = child_alert
        self.child_page.save()

        # Child should display parent's cascading alert
        self.assertEqual(self.child_page.global_alert, parent_alert)

    def test_grandchild_inherits_from_grandparent_cascade(self):
        """Cascade should work through multiple levels of hierarchy for themed alerts"""
        grandparent_alert = ThemedAlert.objects.create(
            name="Grandparent Alert",
            title="Grandparent",
            message="Grandparent message",
            active=True,
            cascade=True,
            theme=ThemedAlert.AlertThemeChoices.YELLOW,
        )

        self.parent_page.themed_alert = grandparent_alert
        self.parent_page.save()

        # Grandchild should inherit cascading alert
        self.assertEqual(self.grandchild_page.global_alert, grandparent_alert)
