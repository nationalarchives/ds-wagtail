from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.crypto import get_random_string
from django_otp.models import Device

from app.core.forms.auth import HtmlPasswordResetForm


class Command(BaseCommand):
    help = "Manage 2FA devices."  # TODO make better

    def add_arguments(self, parser):
        parser.add_argument(
            "--target-email", required=True, help="Email of the user to be reset."
        )
        parser.add_argument(
            "--admin-username", required=True, help="Admin/username performing reset."
        )
        parser.add_argument(
            "--reason",
            default="Your 2FA devices have been removed from your account. Please reset your password. \n Note: Any active sessions you may have had have also been deleted.",
            help="Optional reason to include in the notification email",
        )

    # be authenticated with an admin account
    def check_admin_authentication(self, admin_username):
        admin_user = User.objects.filter(
            **{User.USERNAME_FIELD: admin_username}
        ).first()
        if not admin_user:
            raise CommandError("Admin authentication failed.")

        if not admin_user.is_active or not (
            admin_user.is_superuser or admin_user.has_perm("wagtailadmin.access_admin")
        ):
            raise CommandError("Authenticated user does not have Wagtail admin access.")

    def get_target_user(self, target_email):
        target_user = User.objects.filter(email=target_email).first()
        if not target_user:
            raise CommandError(f"No user found for email {target_email}")

        if not target_user.is_active:
            raise CommandError("Target user is inactive.")
        self.stdout.write(f"Target user found: {target_user} {target_user.email}")
        return target_user

    # remove all 2FA devices
    def remove_devices(self, target_user):
        devices = Device.objects.filter(user=target_user)
        self.stdout.write(f"2FA devices to remove: {devices.count()}")
        # devices.delete()

    # reset the password
    def reset_password(self, target_user):
        random_password = get_random_string(40)
        target_user.password = make_password(random_password)
        target_user.save(update_fields=["password"])

    # remove all active sessions for that user
    def remove_all_active_sessions(self, target_user):
        active_session_keys = []
        for session in Session.objects.filter(expire_date__gte=timezone.now()):
            data = session.get_decoded()
            if str(data.get("_auth_user_id")) == str(target_user.pk):
                active_session_keys.append(session.session_key)
        session_count = len(active_session_keys)
        self.stdout.write(f"Active sessions to revoke: {session_count}")
        # todo delete sessions still

    # send them an email
    def send_email(self, target_user, reason):

        # TODO: make this email nice to read and include reason
        form = HtmlPasswordResetForm({"email": target_user.email}, {"reason": reason})
        if not form.is_valid():
            raise CommandError("Could not prepare password reset email for target user")

        form.save(
            from_email=settings.DEFAULT_FROM_EMAIL,
            request=None,
            use_https=True,
        )

    def handle(self, *args, **options):
        target_email = options["target_email"].strip().lower()
        admin_username = options["admin_username"].strip()
        reason = options["reason"]

        if self.check_admin_authentication(admin_username):
            target_user = self.get_target_user(target_email)
            self.remove_devices(target_user)
            self.reset_password(target_user)
            self.remove_all_active_sessions(target_user)
            self.send_email(target_user, reason)
