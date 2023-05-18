from django.db import migrations

from etna.ciim.exceptions import KongAPIError


def migrate_forwards(apps, schema_editor):
    Highlight = apps.get_model("highlights", "Highlight")
    Image = apps.get_model("images", "CustomImage")

    to_create = []

    for image in Image.objects.exclude(record__isnull=True).exclude(record=""):
        try:
            to_create.append(
                Highlight(
                    record=image.record,
                    reference_number=image.record.reference_number,
                    title=image.title,
                    teaser_image=image,
                    dates=image.record_dates,
                    description=image.description,
                )
            )
        except (KongAPIError, AttributeError):
            pass
    Highlight.objects.bulk_create(to_create)


def migrate_backwards(apps, schema_editor):
    Highlight = apps.get_model("highlights", "Highlight")
    Highlight.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("highlights", "0004_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_forwards, migrate_backwards),
    ]
