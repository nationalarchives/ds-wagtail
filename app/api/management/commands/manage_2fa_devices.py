import logging

import django_otp
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand, CommandError
from django.template import loader
from django.utils import timezone
from django.utils.crypto import get_random_string
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice

from app.core.forms.auth import HtmlPasswordResetForm, send_recovery_codes_email
from app.api.management.commands.manage_2fa_helpers import (
    find_matching_users,
    format_device_name,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "List users without 2FA, remove or reset 2FA devices, reset password, revoke sessions, and notify a user."

    def add_arguments(self, parser):


        parser.add_argument(
            "--target-email",
            help="Email of the user account to be reset.",
        )
        parser.add_argument(
            "--reason",
            default="",
            help="Optional additional reason to include in the notification email",
        )
        parser.set_defaults(execute=False)
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Perform destructive actions (default: dry-run)",
        )
        parser.add_argument(
            "--only-reset-recovery-codes",
            action="store_true",
            help="When used with --execute, delete StaticDevice(s) (recovery codes) for the user.",
        )


    def get_target_user(self, target_email):
        self.stdout.write("\n--- Step 1: Locate Target User ---")
        target_user = User.objects.filter(email__iexact=target_email).first()
        if not target_user:
            logger.warning("No user found with email: %s", target_email)
            raise CommandError(
                self.style.ERROR(f"❌ No user found with email: {target_email}")
            )

        if not target_user.is_active:
            logger.warning("Target user %s is inactive", target_email)
            raise CommandError(self.style.ERROR("❌ Target user is inactive."))

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Target user found: {target_user.email} (ID: {target_user.pk})"
            )
        )
        logger.info("Target user found: %s (ID: %s)", target_user.email, target_user.pk)
        return target_user

    def _format_device_name(self, label, device):
        return format_device_name(label, device)

    def _remove_devices(self, target_user):
        self.stdout.write("\n--- Step 2: Remove 2FA Devices ---")
        if self.only_reset_recovery_codes:
            device_sets = [
                ("Recovery codes", StaticDevice.objects.filter(user=target_user))
            ]
        else:
            device_sets = [
                ("TOTP", TOTPDevice.objects.filter(user=target_user)),
                ("Recovery codes", StaticDevice.objects.filter(user=target_user)),
            ]

        total_count = sum(devices.count() for _, devices in device_sets)

        if total_count == 0:
            self.stdout.write(self.style.WARNING("⚠ No 2FA devices found."))
            logger.info("No 2FA devices found for user %s", target_user.pk)
            return

        self.stdout.write(f"Found {total_count} device(s) to remove:")
        logger.info(
            "Found %d device(s) to remove for user %s", total_count, target_user.pk
        )
        for label, devices in device_sets:
            for device in devices:
                self.stdout.write(self._format_device_name(label, device))

        if self.execute:
            if self.only_reset_recovery_codes:
                recovery_qs = device_sets[0][1]
                device_count = recovery_qs.count()
                deleted_rows = recovery_qs.delete()[0]
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Deleted {device_count} StaticDevice(s) ({deleted_rows} rows)."
                    )
                )
                logger.info(
                    "Deleted %d StaticDevice(s) (%d rows) for user %s (execute=%s)",
                    device_count,
                    deleted_rows,
                    target_user.pk,
                    self.execute,
                )
            else:
                device_count = sum(devices.count() for _, devices in device_sets)
                deleted_rows = sum(devices.delete()[0] for _, devices in device_sets)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Deleted {device_count} 2FA device(s) ({deleted_rows} rows)."
                    )
                )
                logger.info(
                    "Deleted %d 2FA device(s) (%d rows) for user %s (execute=%s)",
                    device_count,
                    deleted_rows,
                    target_user.pk,
                    self.execute,
                )
        else:
            if self.only_reset_recovery_codes:
                self.stdout.write(
                    self.style.NOTICE(
                        f"DRY RUN: would delete {device_sets[0][1].count()} StaticDevice(s)."
                    )
                )
                logger.info(
                    "DRY RUN: would delete %d StaticDevice(s) for user %s",
                    device_sets[0][1].count(),
                    target_user.pk,
                )
            else:
                self.stdout.write(
                    self.style.NOTICE(
                        f"DRY RUN: would delete {total_count} 2FA device(s)."
                    )
                )
                logger.info(
                    "DRY RUN: would delete %d 2FA device(s) for user %s",
                    total_count,
                    target_user.pk,
                )

    def _reset_password(self, target_user):
        self.stdout.write("\n--- Step 3: Reset Password ---")
        if self.execute:
            random_password = get_random_string(40)
            target_user.password = make_password(random_password)
            target_user.save(update_fields=["password"])
            self.stdout.write(
                self.style.SUCCESS("✓ Password has been reset to a random value.")
            )
            logger.info(
                "Password reset for user %s (execute=%s)", target_user.pk, self.execute
            )
        else:
            self.stdout.write(
                self.style.NOTICE(
                    "DRY RUN: would reset the user's password to a random value."
                )
            )
            logger.info("DRY RUN: would reset password for user %s", target_user.pk)

    def _remove_all_active_sessions(self, target_user):
        self.stdout.write("\n--- Step 4: Revoke Active Sessions ---")
        active_session_keys = []
        for session in Session.objects.filter(expire_date__gte=timezone.now()):
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
            logger.info("No active sessions found for user %s", target_user.pk)
            return

        self.stdout.write(f"Found {session_count} active session(s). Revoking...")
        logger.info(
            "Found %d active sessions for user %s", session_count, target_user.pk
        )
        if self.execute:
            deleted_count, _ = Session.objects.filter(
                session_key__in=active_session_keys
            ).delete()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Deleted {deleted_count} session(s).")
            )
            logger.info(
                "Deleted %d session(s) for user %s", deleted_count, target_user.pk
            )
        else:
            self.stdout.write(
                self.style.NOTICE(f"DRY RUN: would delete {session_count} session(s).")
            )
            logger.info(
                "DRY RUN: would delete %d session(s) for user %s",
                session_count,
                target_user.pk,
            )

    def _send_password_reset_email(self, target_user, reason):
        self.stdout.write("\n--- Step 5: Send Notification Email ---")
        try:
            form = HtmlPasswordResetForm({"email": target_user.email})
            form.email_template_name = (
                "wagtailadmin/account/password_reset/email_plain_2fa.txt"
            )
            form.html_email_template_name = (
                "wagtailadmin/account/password_reset/password_reset_email_2fa.html"
            )
            if not form.is_valid():
                raise CommandError(
                    self.style.ERROR(
                        "❌ Could not prepare password reset email for target user"
                    )
                )

            extra = {"reason": reason} if reason else {}

            if self.execute:
                form.save(
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    request=None,
                    use_https=True,
                    extra_email_context=extra,
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Password reset email sent to {target_user.email}"
                    )
                )
                logger.info(
                    "Password reset email sent to %s for user %s",
                    target_user.email,
                    target_user.pk,
                )
            else:
                # dry-run: render templates and print them
                def _dry_send_mail(
                    subject_template_name,
                    email_template_name,
                    context,
                    from_email,
                    to_email,
                    html_email_template_name=None,
                    encoding="utf-8",
                ):
                    merged = {**(context or {}), **extra}
                    subject = "The National Archives: Password Reset (Two-Factor Authentication)"
                    plain = loader.render_to_string(email_template_name, merged)
                    self.stdout.write(
                        self.style.NOTICE(f"DRY RUN: Email to {to_email}")
                    )
                    self.stdout.write(self.style.NOTICE(f"Subject: {subject}"))
                    self.stdout.write("Plain body:")
                    self.stdout.write(plain)
                    if html_email_template_name:
                        html_ctx = {
                            **merged,
                            "reset_url": form._build_reset_url(merged),
                        }
                        html = loader.render_to_string(
                            html_email_template_name, html_ctx
                        )
                        self.stdout.write("HTML body:")
                        self.stdout.write(html)

                form.send_mail = _dry_send_mail
                form.save(
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    request=None,
                    use_https=True,
                    extra_email_context=extra,
                )
                self.stdout.write(
                    self.style.NOTICE(
                        f"DRY RUN: would send password reset email to {target_user.email}"
                    )
                )
                logger.info(
                    "DRY RUN: would send password reset email to %s for user %s",
                    target_user.email,
                    target_user.pk,
                )
        except Exception as e:
            logger.exception(
                "Failed to send password reset email to user %s", target_user.pk
            )
            self.stdout.write(self.style.ERROR(f"❌ Failed to send email: {e}"))
            raise

    # Email rendering/sending delegated to app.core.forms.auth.send_recovery_codes_email
    def _send_recovery_codes_notification(self, target_user, reason):
        self.stdout.write("\n--- Step 5: Send Recovery Codes Email ---")
        try:
            email = send_recovery_codes_email(
                target_user, reason, execute=self.execute
            )
            if email.get("sent"):
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Recovery codes notification sent to {target_user.email}"
                    )
                )
                logger.info(
                    "Recovery codes notification sent to %s for user %s",
                    target_user.email,
                    target_user.pk,
                )
            else:
                self.stdout.write(
                    self.style.NOTICE(f"DRY RUN: Email to {target_user.email}")
                )
                self.stdout.write(self.style.NOTICE(f"Subject: {email.get('subject')}"))
                if email.get("reason"):
                    self.stdout.write(self.style.NOTICE(f"Reason: {email['reason']}"))

                # Print rendered bodies when available (dry-run)
                plain = email.get("plain")
                html = email.get("html")
                if plain:
                    self.stdout.write("Plain body:")
                    self.stdout.write(plain)
                if html:
                    self.stdout.write("HTML body:")
                    self.stdout.write(html)

                logger.info(
                    "DRY RUN: recovery codes email prepared for %s (subject=%s)",
                    target_user.email,
                    email.get("subject"),
                )
        except Exception as e:
            logger.exception(
                "Failed to send recovery codes email to user %s", target_user.pk
            )
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to send recovery codes email: {e}")
            )
            raise

    def handle(self, *args, **options):
        if options.get("list_missing_2fa"):
            return self.list_users_missing_2fa()

        if options.get("list_missing_recovery_codes"):
            return self.list_users_missing_recovery_codes()

        target_email = options.get("target_email")
        reason = options.get("reason")

        if not target_email:
            raise CommandError(
                self.style.ERROR(
                    "❌ --target-email is required unless using a list flag."
                )
            )

        target_email = target_email.strip().lower()

        try:
            self.stdout.write(self.style.NOTICE("=" * 60))
            self.stdout.write(
                self.style.NOTICE(
                    "Two-Factor Authentication (2FA) Device & User Security Reset"
                )
            )
            self.stdout.write(self.style.NOTICE("=" * 60))
            target_user = self.get_target_user(target_email)

            self.execute = bool(options.get("execute"))
            self.only_reset_recovery_codes = bool(
                options.get("only_reset_recovery_codes")
            )
            self._remove_devices(target_user)
            if self.only_reset_recovery_codes:
                self._send_recovery_codes_notification(target_user, reason)
            else:
                self._reset_password(target_user)
                self._remove_all_active_sessions(target_user)
                self._send_password_reset_email(target_user, reason)

            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("✓ All steps completed successfully!"))
            self.stdout.write("=" * 60)
            self.stdout.write(f"User {target_user.email} has been reset.\n")
            logger.info(
                "User %s has been reset (execute=%s)", target_user.email, self.execute
            )

        except CommandError as e:
            self.stdout.write(f"\n{e}\n")
            raise
