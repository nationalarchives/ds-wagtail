from datetime import timedelta

from app.alerts.models import Alert
from app.alerts.serializers import AlertSerializer
from app.generic_pages.factories import GeneralPageFactory
from django.core.exceptions import ValidationError
from django.utils import timezone
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase


class AlertActivityTests(WagtailPageTestCase):
    def test_active_alert_without_expiry_is_active(self):
        alert = Alert.objects.create(
            name="No Expiry Alert",
            title="Important",
            message="This is a test",
            active=True,
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        self.assertTrue(alert.is_active_now)

    def test_active_alert_with_future_expiry_is_active(self):
        alert = Alert.objects.create(
            name="Future Expiry Alert",
            title="Important",
            message="This is a test",
            active=True,
            active_to=timezone.now() + timedelta(hours=1),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        self.assertTrue(alert.is_active_now)

    def test_active_alert_with_past_expiry_is_inactive(self):
        alert = Alert.objects.create(
            name="Past Expiry Alert",
            title="Important",
            message="This is a test",
            active=True,
            active_to=timezone.now() - timedelta(hours=1),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        self.assertFalse(alert.is_active_now)
        self.assertTrue(alert.active)
        alert.refresh_from_db()
        self.assertTrue(alert.active)

    def test_inactive_alert_with_future_expiry_is_inactive(self):
        alert = Alert.objects.create(
            name="Inactive Alert",
            title="Important",
            message="This is a test",
            active=False,
            active_to=timezone.now() + timedelta(hours=1),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        self.assertFalse(alert.is_active_now)

    def test_unpublished_alert_with_past_schedule_is_inactive(self):
        alert = Alert.objects.create(
            name="Unpublished Scheduled Alert",
            title="Important",
            message="This is a test",
            active=False,
            active_from=timezone.now() - timedelta(hours=1),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        self.assertFalse(alert.is_active_now)
        self.assertFalse(alert.active)
        alert.refresh_from_db()
        self.assertFalse(alert.active)

    def test_active_alert_with_future_schedule_is_inactive(self):
        alert = Alert.objects.create(
            name="Scheduled Future Alert",
            title="Important",
            message="This is a test",
            active=True,
            active_from=timezone.now() + timedelta(hours=1),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        self.assertFalse(alert.is_active_now)
        self.assertTrue(alert.active)
        alert.refresh_from_db()
        self.assertTrue(alert.active)

    def test_unpublished_alert_with_open_window_is_inactive(self):
        alert = Alert.objects.create(
            name="Unpublished Window Alert",
            title="Important",
            message="This is a test",
            active=False,
            active_from=timezone.now() - timedelta(hours=1),
            active_to=timezone.now() + timedelta(hours=1),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        self.assertFalse(alert.is_active_now)
        alert.refresh_from_db()
        self.assertFalse(alert.active)

    def test_scheduled_alert_with_past_expiry_is_inactive(self):
        alert = Alert.objects.create(
            name="Scheduled Expired Alert",
            title="Important",
            message="This is a test",
            active=False,
            active_from=timezone.now() - timedelta(hours=2),
            active_to=timezone.now() - timedelta(hours=1),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        self.assertFalse(alert.is_active_now)
        alert.refresh_from_db()
        self.assertFalse(alert.active)

    def test_serializer_excludes_expired_alert(self):
        alert = Alert.objects.create(
            name="Expired Alert",
            title="Important",
            message="This is a test",
            active=True,
            active_to=timezone.now() - timedelta(hours=1),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        self.assertIsNone(AlertSerializer().to_representation(alert))

    def test_serializer_excludes_not_yet_scheduled_alert(self):
        alert = Alert.objects.create(
            name="Not Yet Scheduled Alert",
            title="Important",
            message="This is a test",
            active=True,
            active_from=timezone.now() + timedelta(hours=1),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        self.assertIsNone(AlertSerializer().to_representation(alert))

    def test_validation_passes_when_active_with_future_schedule_and_expiry(self):
        alert = Alert(
            name="Valid Published Future Window Alert",
            title="Important",
            message="This is a test",
            active=True,
            active_from=timezone.now() + timedelta(hours=1),
            active_to=timezone.now() + timedelta(hours=2),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        alert.full_clean()

    def test_validation_passes_when_inactive_with_future_schedule_and_expiry(self):
        alert = Alert(
            name="Valid Future Window Alert",
            title="Important",
            message="This is a test",
            active=False,
            active_from=timezone.now() + timedelta(hours=1),
            active_to=timezone.now() + timedelta(hours=2),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        alert.full_clean()

    def test_validation_fails_when_schedule_is_in_the_past(self):
        alert = Alert(
            name="Past Schedule Alert",
            title="Important",
            message="This is a test",
            active=False,
            active_from=timezone.now() - timedelta(hours=1),
            active_to=None,
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        with self.assertRaises(ValidationError) as context:
            alert.full_clean()

        self.assertTrue(
            any(
                "Scheduled date cannot be in the past." in message
                for message in context.exception.message_dict["active_from"]
            )
        )

    def test_validation_passes_when_active_before_schedule_with_no_expiry(self):
        alert = Alert(
            name="Valid Published Future Schedule Alert",
            title="Important",
            message="This is a test",
            active=True,
            active_from=timezone.now() + timedelta(hours=1),
            active_to=None,
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        alert.full_clean()

    def test_validation_passes_when_inactive_with_future_schedule_and_no_expiry(self):
        alert = Alert(
            name="Valid Future Schedule Only Alert",
            title="Important",
            message="This is a test",
            active=False,
            active_from=timezone.now() + timedelta(hours=1),
            active_to=None,
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        alert.full_clean()

    def test_validation_passes_when_active_after_expiry_with_no_schedule(self):
        alert = Alert(
            name="Valid Published Expired Alert",
            title="Important",
            message="This is a test",
            active=True,
            active_from=None,
            active_to=timezone.now() - timedelta(hours=1),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        alert.full_clean()

    def test_validation_passes_when_active_before_expiry_with_no_schedule(self):
        alert = Alert(
            name="Valid Expiry Only Alert",
            title="Important",
            message="This is a test",
            active=True,
            active_from=None,
            active_to=timezone.now() + timedelta(hours=1),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        alert.full_clean()

    def test_validation_fails_when_schedule_is_not_before_expiry(self):
        alert = Alert(
            name="Invalid Window Order Alert",
            title="Important",
            message="This is a test",
            active=False,
            active_from=timezone.now() + timedelta(hours=2),
            active_to=timezone.now() + timedelta(hours=1),
            alert_level=Alert.AlertLevelChoices.MEDIUM,
        )

        with self.assertRaises(ValidationError) as context:
            alert.full_clean()

        self.assertIn(
            "Expiry date must be later than the scheduled date.",
            context.exception.message_dict["active_to"],
        )


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

    def test_expired_parent_cascade_does_not_override_child(self):
        """Expired parent alert with cascade should not override child's active alert"""
        parent_alert = Alert.objects.create(
            name="Parent Alert",
            title="Parent",
            message="Parent message",
            active=True,
            cascade=True,
            active_to=timezone.now() - timedelta(hours=1),
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

        self.assertEqual(self.child_page.global_alert, child_alert)
