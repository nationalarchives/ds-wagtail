# etna:allowAlterField

from django.db import migrations


AGE_RANGE_UPDATES = {
    "5-7": "5–7",
    "7-11": "7–11",
    "11-14": "11–14",
    "14-16": "14–16",
    "16-18": "16–18",
}


def update_keystage_age_ranges(apps, schema_editor):
    KeyStage = apps.get_model("education", "KeyStage")

    for old_age_range, new_age_range in AGE_RANGE_UPDATES.items():
        KeyStage.objects.filter(age_range=old_age_range).update(age_range=new_age_range)


def revert_keystage_age_ranges(apps, schema_editor):
    KeyStage = apps.get_model("education", "KeyStage")

    for old_age_range, new_age_range in AGE_RANGE_UPDATES.items():
        KeyStage.objects.filter(age_range=new_age_range).update(age_range=old_age_range)


class Migration(migrations.Migration):
    dependencies = [
        ("education", "0007_teachingresourcepage_partner_logos_and_more"),
    ]

    operations = [
        migrations.RunPython(update_keystage_age_ranges, revert_keystage_age_ranges),
    ]