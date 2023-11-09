from django.db import migrations
from django.db.models.query import F
from django.utils import timezone


def migrate_forwards(apps, schema_editor):
    now = timezone.now()
    FeedbackPrompt = apps.get_model("feedback", "FeedbackPrompt")
    FeedbackPrompt.objects.all().update(
        live_revision=F("latest_revision"),
        first_published_at=now,
        last_published_at=now,
    )


def migrate_backwards(apps, schema_editor):
    FeedbackPrompt = apps.get_model("feedback", "FeedbackPrompt")
    FeedbackPrompt.objects.all().update(
        live_revision=None, first_published_at=None, last_published_at=None
    )


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0002_add_default_prompt"),
    ]

    operations = [
        migrations.RunPython(migrate_forwards, migrate_backwards),
    ]
