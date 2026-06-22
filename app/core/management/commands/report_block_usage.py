import json

from django.core.management.base import BaseCommand

from app.core.block_usage import get_block_usage


class Command(BaseCommand):
    help = "Generate a report of block usage across all StreamFields in the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--format",
            type=str,
            default="text",
            choices=["text", "json", "csv"],
            help="Output format for the report (default: text)",
        )
        parser.add_argument(
            "--field",
            type=str,
            help="Specific StreamField to analyze (e.g., 'body', 'featured_pages')",
        )
        parser.add_argument(
            "--output",
            type=str,
            help="Write report to file instead of stdout",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show verbose debug output",
        )

    def handle(self, *args, **options):
        verbose = options.get("verbose", False)
        block_usage = get_block_usage(
            specific_field=options.get("field"),
            verbose=verbose,
            log=self.stdout.write,
            error_log=self._log_processing_error,
        )

        if not block_usage:
            self.stdout.write(self.style.WARNING("No blocks found in StreamFields"))
            return

        output = self.format_output(block_usage, options["format"])

        if options["output"]:
            with open(options["output"], "w") as f:
                f.write(output)
            self.stdout.write(
                self.style.SUCCESS(f"Report written to {options['output']}")
            )
        else:
            self.stdout.write(output)

    def _log_processing_error(self, model, field, exc):
        self.stdout.write(
            self.style.WARNING(
                f"Error processing {model.__name__}.{field.name}: {str(exc)}"
            )
        )

    def format_output(self, block_usage, format_type):
        """Format the block usage data for output"""
        if format_type == "json":
            return json.dumps(block_usage, indent=2)

        elif format_type == "csv":
            lines = ["Field,Block Type,Count"]
            for field_name, blocks in sorted(block_usage.items()):
                for block_type, count in sorted(
                    blocks.items(), key=lambda x: x[1], reverse=True
                ):
                    lines.append(f'"{field_name}","{block_type}",{count}')
            return "\n".join(lines)

        else:  # text format
            lines = ["Block Usage Report\n" + "=" * 80]

            total_blocks = 0
            for field_name in sorted(block_usage.keys()):
                blocks = block_usage[field_name]
                lines.append(f"\n{field_name}")
                lines.append("-" * 80)

                for block_type, count in sorted(
                    blocks.items(), key=lambda x: x[1], reverse=True
                ):
                    lines.append(f"  {block_type:<50} {count:>10}")
                    total_blocks += count

            lines.append("\n" + "=" * 80)
            lines.append(f"Total blocks: {total_blocks}")

            return "\n".join(lines)
