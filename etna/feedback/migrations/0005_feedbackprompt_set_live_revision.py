from django.db import migrations
from django.db.models.query import F


def migrate_forwards(apps, schema_editor):
    FeedbackPrompt = apps.get_model("feedback", "FeedbackPrompt")
    FeedbackPrompt.objects.all().update(live_revision=F("latest_revision"))


def migrate_backwards(apps, schema_editor):
    FeedbackPrompt = apps.get_model("feedback", "FeedbackPrompt")
    FeedbackPrompt.objects.all().update(live_revision=None)


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0004_feedbackprompt_use_draftstatemixin"),
    ]

    operations = [
        migrations.RunPython(migrate_forwards, migrate_backwards),
    ]
