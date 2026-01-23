"""
Management command to sync archive data from external JSON source.

- Processes in batches: validates entries → saves → clears
- Assumes wamId is unique
- Full JSON dataset remains in memory throughout processing
- Memory scales with dataset size. Local testing shows:
    - ~200MB peak for 15k entries
    - ~400MB peak for 78k entries
- Memory usage spikes during JSON load, but then flat during batch processing

Expected Schema of input:
    [
        {
            "profileName": str,
            "entryUrl": str,
            "archiveLink": str,
            "domainType": str,
            "firstCapture": str,
            "firstCaptureDisplay": str,
            "latestCapture": str,
            "latestCaptureDisplay": str,
            "ongoing": bool,
            "wamId": int,
            "wamLink": str,
            "parentId": int | None,
            "generatedOn": str,
            "currentDepartments": list,
            "previousDepartments": list,
            "description": str
        },
        {...}
    ]

Saved fields:
    [
        "profileName": str,
        "entryUrl": str,
        "archiveLink": str,
        "domainType": str,
        "firstCaptureDisplay": str,
        "latestCaptureDisplay": str,
        "ongoing": bool,
        "wamId": int,
        "description": str
    ]

Usage:
    python manage.py sync_archive_data --url https://example.com/data.json
    python manage.py sync_archive_data  # Uses ARCHIVE_JSON_URL environment variable
    python manage.py sync_archive_data --dry-run  # Validates first 100 entries only
"""

import json
import logging
import os

import requests
from app.ukgwa.models import ArchiveRecord
from app.ukgwa.schemas import ArchiveRecordSchema
from django.core.management.base import BaseCommand
from django.db import DatabaseError, transaction
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Sync archive data from external JSON source with hash-based change detection"
    )

    DRY_RUN_LIMIT = 100  # Number of entries to process in dry-run mode

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            type=str,
            help="URL to fetch JSON data from (otherwise uses ARCHIVE_JSON_URL env var)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and report without saving to database (processes first 100 entries only)",
        )
        parser.add_argument(
            "--validation-batch-size",
            type=int,
            default=5000,
            help="Number of entries to validate at once before saving (default: 5000)",
        )
        parser.add_argument(
            "--commit-batch-size",
            type=int,
            default=1000,
            help="Number of entries per database transaction (default: 1000)",
        )

    def handle(self, **options):
        stats = {
            "total": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "deleted": 0,
            "validation_errors": 0,
            "database_errors": 0,
        }

        validation_batch_size = options["validation_batch_size"]
        commit_batch_size = options["commit_batch_size"]

        url = options.get("url") or os.environ.get("ARCHIVE_JSON_URL")
        if not url:
            self.stdout.write(
                self.style.ERROR(
                    "No data source specified. Use --url or set ARCHIVE_JSON_URL environment variable"
                )
            )
            return

        # Load JSON data
        try:
            raw_data = self.load_data(url)
        except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to load archive data from {url}: {str(e)}")
            self.stdout.write(self.style.ERROR(f"Failed to load data: {e}"))
            return

        stats["total"] = len(raw_data)

        logger.info(
            f"Starting archive data sync: {stats['total']} entries, dry_run={options['dry_run']}"
        )

        # Handle dry run
        if options["dry_run"]:
            self._handle_dry_run(raw_data, stats["total"])
            return

        # Full sync
        self.stdout.write(
            f"Processing {stats['total']} entries in batches of {validation_batch_size}...\n"
        )

        source_wam_ids = []
        total_validated = 0

        # Process data in validation batches
        for batch_start in range(0, len(raw_data), validation_batch_size):
            batch_end = min(batch_start + validation_batch_size, len(raw_data))
            batch_data = raw_data[batch_start:batch_end]
            batch_num = (batch_start // validation_batch_size) + 1
            total_batches = (
                len(raw_data) + validation_batch_size - 1
            ) // validation_batch_size

            self.stdout.write(
                f"\n--- Batch {batch_num}/{total_batches}: Validating entries {batch_start + 1}-{batch_end} ---"
            )

            # Validate batch
            validated_entries, validation_errors = self._validate_entries(batch_data)
            stats["validation_errors"] += validation_errors
            batch_valid_count = len(validated_entries)
            total_validated += batch_valid_count

            self.stdout.write(f"Validated {batch_valid_count} entries")

            if batch_valid_count > 0:
                # Collect wam_ids for deletion later
                batch_wam_ids = [entry.wam_id for entry in validated_entries]
                source_wam_ids.extend(batch_wam_ids)

                # Save batch immediately
                self.stdout.write(f"Saving {batch_valid_count} entries to database...")
                save_results = self._save_entries(
                    validated_entries, batch_valid_count, commit_batch_size
                )

                # Accumulate stats
                stats["created"] += save_results["created"]
                stats["updated"] += save_results["updated"]
                stats["skipped"] += save_results["skipped"]
                stats["database_errors"] += save_results["database_errors"]

        # Summary after all batches
        self.stdout.write(
            self.style.SUCCESS(
                f"\n\nValidation complete: {total_validated} valid entries"
            )
        )
        if stats["validation_errors"] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Skipped {stats['validation_errors']} entries due to validation errors"
                )
            )

        # Delete entries not in source
        self.stdout.write("\nRemoving entries not in source...")
        with transaction.atomic():
            try:
                deleted_count, _ = ArchiveRecord.objects.exclude(
                    wam_id__in=source_wam_ids
                ).delete()
                stats["deleted"] = deleted_count

                if deleted_count > 0:
                    self.stdout.write(f"Deleted {deleted_count} entries not in source")
            except DatabaseError as e:
                logger.error(f"Database error deleting removed entries: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"Failed to delete removed entries: {e}")
                )

        # Clear caches after successful sync
        self.stdout.write("\nClearing archive caches...")
        ArchiveRecord.clear_cache()
        self.stdout.write("Caches cleared")

        logger.info(
            f"Archive data sync completed: {stats['total']} total, "
            f"{stats['created']} created, {stats['updated']} updated, "
            f"{stats['skipped']} skipped, {stats['deleted']} deleted, "
            f"{stats['validation_errors']} validation errors, "
            f"{stats['database_errors']} database errors"
        )
        self.stdout.write(
            self.style.SUCCESS(
                "\nProcessing complete. Check logs for detailed statistics."
            )
        )

    def _handle_dry_run(self, raw_data, total_count):
        """
        Validate a limited sample and display summary, without database transactions.
        """
        sample_data = raw_data[: self.DRY_RUN_LIMIT]
        self.stdout.write(
            self.style.WARNING(
                f"Dry run mode: processing first {len(sample_data)} of {total_count} entries\n"
            )
        )

        # Validate sample
        validated_entries, validation_errors = self._validate_entries(sample_data)
        total_valid_entries = len(validated_entries)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nValidation complete: {total_valid_entries} valid entries"
            )
        )
        if validation_errors > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Skipped {validation_errors} entries due to validation errors"
                )
            )

        # Output summary
        self.stdout.write(
            f"\n{'=' * 60}"
            f"\n{self.style.SUCCESS('Dry Run Complete')}\n"
            f"{'=' * 60}\n"
            f"Validated: {total_valid_entries}/{len(sample_data)} entries from sample\n"
            f"Total in source: {total_count} entries\n"
            f"Validation errors: {validation_errors}\n"
            f"{'=' * 60}\n"
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Would process {total_valid_entries} valid entries in full sync"
            )
        )

    def _validate_entries(self, raw_data):
        """
        Validate raw JSON entries using Pydantic schema.

        Returns:
            tuple: (validated_entries, validation_error_count)
        """
        validated_entries = []
        validation_errors = 0

        for idx, raw_entry in enumerate(raw_data, 1):
            try:
                # Validate with Pydantic (computes hash, sort_name, first_character)
                validated = ArchiveRecordSchema(**raw_entry)
                validated_entries.append(validated)

            except ValidationError as e:
                validation_errors += 1
                wam_id = raw_entry.get("wamId", "unknown")

                # Format error details for readable output
                error_details = ", ".join(
                    [
                        f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
                        for err in e.errors()
                    ]
                )
                logger.warning(
                    f"Validation failed for entry {idx} (wam_id: {wam_id}): {error_details}"
                )

        return validated_entries, validation_errors

    def _save_entries(self, validated_entries, total_valid_entries, commit_batch_size):
        """
        Save validated entries to database in batches. Each batch commits independently
        with savepoints for individual entry error handling.

        Args:
            validated_entries: List of validated ArchiveRecordSchema objects
            total_valid_entries: Total count of validated entries (for progress indicator)
            commit_batch_size: Number of entries per database transaction

        Returns:
            dict: {
                "created": int,
                "updated": int,
                "skipped": int,
                "database_errors": int
            }
        """
        save_stats = {"created": 0, "updated": 0, "skipped": 0, "database_errors": 0}

        # Process entries in batches to commit incrementally
        for batch_start in range(0, len(validated_entries), commit_batch_size):
            batch_end = min(
                batch_start + commit_batch_size, len(validated_entries)
            )
            batch = validated_entries[batch_start:batch_end]

            # Batch transaction
            with transaction.atomic():
                for validated in batch:
                    try:
                        # Savepoint to prevent failure breaking the batch
                        with transaction.atomic():
                            result = self.save_entry(validated)
                            save_stats[result] += 1
                    except DatabaseError as e:
                        save_stats["database_errors"] += 1
                        error_msg = str(e)
                        profile_name = (
                            validated.profile_name[:50]
                            if validated.profile_name
                            else "N/A"
                        )

                        logger.error(
                            f"Database error saving entry {validated.wam_id} "
                            f"({profile_name}): {error_msg}"
                        )

                        self.stdout.write(
                            self.style.WARNING(
                                f"  Skipped entry {validated.wam_id} (database error)"
                            )
                        )

                    processed = (
                        save_stats["created"]
                        + save_stats["updated"]
                        + save_stats["skipped"]
                        + save_stats["database_errors"]
                    )
                    if processed % 1000 == 0:
                        self.stdout.write(
                            f"  Processed {processed}/{total_valid_entries}..."
                        )

        return save_stats

    def load_data(self, url):
        """
        Load JSON data from URL.

        Args:
            url: URL to fetch JSON data from

        Returns:
            list: Parsed JSON array of archive entries

        Raises:
            requests.RequestException: If HTTP request fails
            json.JSONDecodeError: If response is not valid JSON
        """
        self.stdout.write(f"Fetching data from {url}...")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.json()

    def save_entry(self, validated: ArchiveRecordSchema):
        """
        Save or update an entry in the database using hash-based change detection to
        avoid unnecessary updates.

        Returns: 'created', 'updated', or 'skipped'
        """
        try:
            existing = ArchiveRecord.objects.get(wam_id=validated.wam_id)

            if existing.record_hash == validated.record_hash:
                return "skipped"

            existing.profile_name = validated.profile_name
            existing.record_url = str(validated.record_url)
            existing.archive_link = str(validated.archive_link)
            existing.domain_type = validated.domain_type
            existing.first_capture_display = validated.first_capture_display
            existing.latest_capture_display = validated.latest_capture_display
            existing.ongoing = validated.ongoing
            existing.sort_name = validated.sort_name
            existing.first_character = validated.first_character
            existing.record_hash = validated.record_hash
            existing.save()

            return "updated"

        except ArchiveRecord.DoesNotExist:
            ArchiveRecord.objects.create(
                wam_id=validated.wam_id,
                profile_name=validated.profile_name,
                record_url=str(validated.record_url),
                archive_link=str(validated.archive_link),
                domain_type=validated.domain_type,
                first_capture_display=validated.first_capture_display,
                latest_capture_display=validated.latest_capture_display,
                ongoing=validated.ongoing,
                sort_name=validated.sort_name,
                first_character=validated.first_character,
                record_hash=validated.record_hash,
            )

            return "created"
