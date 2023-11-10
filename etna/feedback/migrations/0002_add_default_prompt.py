from django.db import migrations
from django.utils import timezone

from etna.feedback.constants import SentimentChoices


def migrate_forwards(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    FeedbackPrompt = apps.get_model("feedback", "FeedbackPrompt")
    Revision = apps.get_model("wagtailcore", "Revision")
    content = {
        "text": "What did you think of this page?",
        "response_options": [
            {
                "id": "654626f0-9abf-42c3-93ef-51dda08d4853",
                "type": "option",
                "value": {
                    "icon": "images/thumb-up.png",
                    "label": "Easy to use",
                    "sentiment": SentimentChoices.POSITIVE,
                    "comment_prompt_text": "Thank you! Can you tell us more about why you answered this way?",
                },
            },
            {
                "id": "de526763-aca3-466e-8dbc-6a262a883556",
                "type": "option",
                "value": {
                    "icon": "images/thumb-down.png",
                    "label": "Hard to use",
                    "sentiment": SentimentChoices.NEGATIVE,
                    "comment_prompt_text": "We're sorry to hear this. Can you tell us more about why you answered this way?",
                },
            },
        ],
        "thank_you_heading": "Thank you for your valuable feedback",
        "thank_you_message": "",
        "continue_link_text": "Return to the previous page",
    }

    # Create the prompt
    prompt = FeedbackPrompt.objects.create(
        public_id="b8c90d12-038f-438c-9fe8-513d0799f270",
        path="/",
        startswith_path=True,
        **content,
    )

    # Create a revision reflective of the current state
    now = timezone.now()
    content_type, _ = ContentType.objects.get_or_create(
        app_label="feedback", model="feedbackprompt"
    )
    content["pk"] = prompt.id
    revision = Revision.objects.create(
        content_type=content_type,
        base_content_type=content_type,
        object_id=prompt.id,
        object_str="What did you think of this page? (default)",
        created_at=now,
        approved_go_live_at=now,
        content=content,
    )

    # Set 'latest_revision' on the prompt
    prompt.latest_revision = revision
    prompt.save()


def migrate_backwards(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    FeedbackPrompt = apps.get_model("feedback", "FeedbackPrompt")
    Revision = apps.get_model("wagtailcore", "Revision")

    # Delete the prompt
    FeedbackPrompt.objects.filter(id=1).delete()

    # Delete any revisions for the prompt
    content_type = ContentType.objects.get(app_label="feedback", model="feedbackprompt")
    Revision.objects.filter(content_type=content_type, object_id=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_forwards, migrate_backwards),
    ]
