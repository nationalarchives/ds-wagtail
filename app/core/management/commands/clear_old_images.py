from datetime import timedelta

from app.images.models import CustomImage
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Clears images that are older than a specified number of days and not used."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=365,
            help="Specify the age in days of images to be cleared. Default is 365 days.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview images that would be deleted without actually deleting them.",
        )

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=options["days"])
        images = CustomImage.objects.filter(created_at__lt=cutoff_date)

        total = images.count()
        deleted_count = 0
        skipped_count = 0
        error_count = 0

        self.stdout.write(f"Found {total} image(s) older than {options['days']} days.")

        for image in images:
            if image.get_usage().count() == 0:
                if options["dry_run"]:
                    self.stdout.write(
                        self.style.WARNING(f"[DRY RUN] Would delete: {image.title}")
                    )
                else:
                    try:
                        self.stdout.write(f"Deleting: {image.title}")
                        image.delete()
                        deleted_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Failed to delete {image.title}: {e}")
                        )
                        error_count += 1
            else:
                skipped_count += 1

        if options["dry_run"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"[DRY RUN] Would delete {deleted_count} unused image(s)."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {deleted_count} unused image(s). "
                    f"Skipped {skipped_count} in use. "
                    f"Errors: {error_count}."
                )
            )
