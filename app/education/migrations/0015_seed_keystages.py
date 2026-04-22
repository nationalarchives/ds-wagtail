from django.db import migrations


KEY_STAGES = [
    ("key-stage-1", "Key Stage 1 (ages 5–7)"),
    ("key-stage-2", "Key Stage 2 (ages 7–11)"),
    ("key-stage-3", "Key Stage 3 (ages 11–14)"),
    ("key-stage-4", "Key Stage 4 (ages 14–16)"),
    ("key-stage-5", "Key Stage 5 (ages 16-18)"),
]


def seed_key_stages(apps, schema_editor):
    KeyStage = apps.get_model("education", "KeyStage")

    for slug, name in KEY_STAGES:
        KeyStage.objects.update_or_create(
            slug=slug,
            defaults={"name": name},
        )


def noop_reverse(apps, schema_editor):
    """Keep seeded key stages when rolling back to avoid data loss."""


class Migration(migrations.Migration):
    dependencies = [
        ("education", "0014_alter_keystage_name_alter_keystage_slug_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_key_stages, noop_reverse),
    ]
