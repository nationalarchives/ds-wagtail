from django.conf import settings
from django.db import migrations
from django.db.models import Count
from django.db.models.functions import Lower


INDEX_NAME = "users_email_login_unique_idx"


def _get_user_model(apps):
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    return apps.get_model(app_label, model_name)


def enforce_email_uniqueness(apps, schema_editor):
    user_model = _get_user_model(apps)

    if not any(field.name == "email" for field in user_model._meta.get_fields()):
        raise RuntimeError("The configured user model does not define an email field.")

    duplicate_emails = (
        user_model.objects.exclude(email="")
        .annotate(email_lower=Lower("email"))
        .values("email_lower")
        .annotate(total=Count("id"))
        .filter(total__gt=1)
    )

    if duplicate_emails.exists():
        examples = ", ".join(item["email_lower"] for item in duplicate_emails[:5])
        raise RuntimeError(
            "Cannot enforce unique email login while duplicate user emails exist. "
            "Please resolve duplicates first. "
            f"Examples: {examples}"
        )

    table_name = schema_editor.quote_name(user_model._meta.db_table)
    schema_editor.execute(
        f"CREATE UNIQUE INDEX IF NOT EXISTS {INDEX_NAME} "
        f"ON {table_name} (LOWER(email)) WHERE email <> ''"
    )


def remove_email_uniqueness(apps, schema_editor):
    schema_editor.execute(f"DROP INDEX IF EXISTS {INDEX_NAME}")


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(enforce_email_uniqueness, remove_email_uniqueness),
    ]
