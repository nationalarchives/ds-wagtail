import urllib.request
import json

from django.core.management.base import BaseCommand, CommandError

from app.search.models import ExternalApplication, ExternalApplicationPage


class Command(BaseCommand):
    help = "Ingest external application data from a JSON API endpoint"

    def add_arguments(self, parser):
        parser.add_argument(
            "url",
            type=str,
            help="The URL of the JSON API endpoint to ingest",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing applications instead of skipping them",
        )

    def handle(self, *args, **options):
        url = options["url"]
        should_update = options["update"]

        self.stdout.write(f"Fetching data from {url}...")

        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
        except urllib.error.URLError as e:
            raise CommandError(f"Failed to fetch data from {url}: {e}")
        except json.JSONDecodeError as e:
            raise CommandError(f"Failed to parse JSON response: {e}")

        if isinstance(data, list):
            applications = data
        else:
            applications = [data]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for app_data in applications:
            title = app_data.get("title")
            if not title:
                self.stderr.write("Skipping entry with no title")
                continue

            pages_data = app_data.get("pages", [])

            app_defaults = {
                "version": app_data.get("version", ""),
                "description": app_data.get("description", ""),
                "base_url": app_data.get("base_url", ""),
                "type_label": app_data.get("type_label", ""),
            }

            first_published_at = app_data.get("first_published_at")
            last_published_at = app_data.get("last_published_at")
            if first_published_at:
                app_defaults["first_published_at"] = first_published_at
            if last_published_at:
                app_defaults["last_published_at"] = last_published_at

            existing = ExternalApplication.objects.filter(title=title).first()

            if existing and not should_update:
                self.stdout.write(
                    self.style.WARNING(f"Skipping existing application: {title}")
                )
                skipped_count += 1
                continue

            if existing and should_update:
                for field, value in app_defaults.items():
                    setattr(existing, field, value)
                existing.save()
                application = existing
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Updated application: {title}"))
            else:
                application = ExternalApplication.objects.create(
                    title=title, **app_defaults
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created application: {title}"))

            for page_data in pages_data:
                page_title = page_data.get("title")
                url_path = page_data.get("url")
                if not page_title or not url_path:
                    self.stderr.write(
                        f"Skipping page with missing title or url in application '{title}'"
                    )
                    continue

                page_defaults = {
                    "description": page_data.get("description") or "",
                    "teaser_image": page_data.get("teaser_image"),
                }

                ExternalApplicationPage.objects.update_or_create(
                    application=application,
                    url_path=url_path,
                    defaults={
                        "title": page_title,
                        **page_defaults,
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}"
            )
        )
