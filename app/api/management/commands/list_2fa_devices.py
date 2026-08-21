import logging

import django_otp
from django.core.management.base import BaseCommand

from app.api.management.commands.manage_2fa_helpers import find_matching_users

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "List users missing 2FA or missing recovery codes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--missing-2fa",
            action="store_true",
            help="List active users who do not have any 2FA devices configured.",
        )
        parser.add_argument(
            "--missing-recovery-codes",
            action="store_true",
            help="List active users who have 2FA devices but no static recovery codes.",
        )

    def handle(self, *args, **options):
        if options.get("missing_2fa"):
            self.stdout.write("\n--- Users without any 2FA devices ---")
            matches = find_matching_users(
                lambda u: not django_otp.user_has_device(u, confirmed=True)
            )
            if not matches:
                self.stdout.write(
                    self.style.WARNING("No users found without 2FA devices.")
                )
                logger.info("No users found without 2FA devices.")
                return
            for u in matches:
                self.stdout.write(f"- {u.email or u.username} (ID: {u.pk})")
            self.stdout.write(
                self.style.SUCCESS(f"Found {len(matches)} user(s) without 2FA devices.")
            )
            logger.info("Found %d user(s) without 2FA devices.", len(matches))

        if options.get("missing_recovery_codes"):
            from django_otp.plugins.otp_static.models import StaticDevice

            self.stdout.write("\n--- Users with 2FA but without recovery codes ---")
            matches = find_matching_users(
                lambda u: (
                    django_otp.user_has_device(u, confirmed=True)
                    and not StaticDevice.objects.filter(user=u).exists()
                )
            )
            if not matches:
                self.stdout.write(
                    self.style.WARNING(
                        "No users found who have 2FA but lack recovery codes."
                    )
                )
                logger.info("No users found who have 2FA but lack recovery codes.")
                return
            for u in matches:
                self.stdout.write(f"- {u.email or u.username} (ID: {u.pk})")
            self.stdout.write(
                self.style.SUCCESS(
                    f"Found {len(matches)} user(s) with 2FA but no recovery codes."
                )
            )
            logger.info(
                "Found %d user(s) with 2FA but no recovery codes.", len(matches)
            )
