from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.crypto import get_random_string
from django_otp.plugins.otp_totp.models import TOTPDevice

from app.core.forms.auth import HtmlPasswordResetForm

User = get_user_model()


class Command(BaseCommand):
    help = "Remove all 2FA devices, reset password, revoke sessions, and notify a user."

    def add_arguments(self, parser):
        parser.add_argument(
            "--target-email", required=True, help="Email of the user to be reset."
        )
        parser.add_argument(
            "--reason",
            default=(
                "Your Two-Factor Authentication (2FA) devices have been removed from your account. Please reset your password.\n\n"
                "Note: Any active sessions you may have had have also been deleted."
            ),
            help="Optional reason to include in the notification email",
        )
        parser.set_defaults(execute=False)
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Perform destructive actions (default: dry-run)",
        )

    def get_target_user(self, target_email):
        self.stdout.write("\n--- Step 2: Locate Target User ---")
        target_user = User.objects.filter(email__iexact=target_email).first()
        if not target_user:
            raise CommandError(
                self.style.ERROR(f"❌ No user found with email: {target_email}")
            )

        if not target_user.is_active:
            raise CommandError(self.style.ERROR("❌ Target user is inactive."))

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Target user found: {target_user.email} (ID: {target_user.pk})"
            )
        )
        return target_user

    def remove_devices(self, target_user):
        self.stdout.write("\n--- Step 3: Remove 2FA Devices ---")
        devices = TOTPDevice.objects.filter(user=target_user)
        device_count = devices.count()
        if device_count == 0:
            self.stdout.write(self.style.WARNING("⚠ No 2FA devices found."))
            return

        self.stdout.write(f"Found {device_count} device(s) to remove:")
        for device in devices:
            try:
                name = getattr(device, "name", "<unnamed>")
            except Exception:
                name = "<error>"
            self.stdout.write(f"  - {name} (ID: {getattr(device, 'id', 'n/a')})")

        if getattr(self, "execute", False):
            deleted_count, _ = devices.delete()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Deleted {deleted_count} 2FA device(s).")
            )
        else:
            self.stdout.write(
                self.style.NOTICE(
                    f"DRY RUN: would delete {device_count} 2FA device(s)."
                )
            )

    def reset_password(self, target_user):
        self.stdout.write("\n--- Step 4: Reset Password ---")
        if getattr(self, "execute", False):
            random_password = get_random_string(40)
            target_user.set_password(random_password)
            target_user.save(update_fields=["password"])
            self.stdout.write(
                self.style.SUCCESS("✓ Password has been reset to a random value.")
            )
        else:
            self.stdout.write(
                self.style.NOTICE(
                    "DRY RUN: would reset the user's password to a random value."
                )
            )

    def remove_all_active_sessions(self, target_user):
        self.stdout.write("\n--- Step 5: Revoke Active Sessions ---")
        active_session_keys = []
        for session in Session.objects.filter(expire_date__gte=timezone.now()).iterator():
            try:
                data = session.get_decoded()
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠ Could not decode session {session.session_key}: {e}"
                    )
                )
                continue

            if str(data.get("_auth_user_id")) == str(target_user.pk):
                active_session_keys.append(session.session_key)

        session_count = len(active_session_keys)
        if session_count == 0:
            self.stdout.write(self.style.WARNING("⚠ No active sessions found."))
            return

        self.stdout.write(f"Found {session_count} active session(s). Revoking...")
        if getattr(self, "execute", False):
            deleted_count, _ = Session.objects.filter(
                session_key__in=active_session_keys
            ).delete()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Deleted {deleted_count} session(s).")
            )
        else:
            self.stdout.write(
                self.style.NOTICE(f"DRY RUN: would delete {session_count} session(s).")
            )

    def send_email(self, target_user, reason):
        self.stdout.write("\n--- Step 6: Send Notification Email ---")
        try:
            form = HtmlPasswordResetForm({"email": target_user.email})
            if not form.is_valid():
                raise CommandError(
                    self.style.ERROR(
                        "❌ Could not prepare password reset email for target user"
                    )
                )
            if getattr(self, "execute", False):
                form.save(
                    from_email=settings.DEFAULT_FROM_EMAIL, request=None, use_https=True
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Password reset email sent to {target_user.email}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.NOTICE(
                        f"DRY RUN: would send password reset email to {target_user.email}"
                    )
                )
                self.stdout.write("HTML body:")
                self.stdout.write(rendered["html"])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to send email: {e}"))
            raise

    def handle(self, *args, **options):
        target_email = options["target_email"].strip().lower()
        reason = options["reason"]

        try:
            self.stdout.write(self.style.NOTICE("=" * 60))
            self.stdout.write(
                self.style.NOTICE(
                    "Two-Factor Authentication (2FA) Device & User Security Reset"
                )
            )
            self.stdout.write(self.style.NOTICE("=" * 60))
            target_user = self.get_target_user(target_email)
            # store execute flag on self for methods to access
            self.execute = bool(options.get("execute"))
            self.remove_devices(target_user)
            self.reset_password(target_user)
            self.remove_all_active_sessions(target_user)
            self.send_email(target_user, reason)

            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("✓ All steps completed successfully!"))
            self.stdout.write("=" * 60)
            self.stdout.write(f"User {target_user.email} has been reset.\n")

        except CommandError as e:
            self.stdout.write(f"\n{e}\n")
            raise
