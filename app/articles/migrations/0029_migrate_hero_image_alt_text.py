from django.db import migrations


def move_alt_text(apps, schema_editor):
    InsightsPage = apps.get_model("articles", "InsightsPage")

    for page in InsightsPage.objects.select_related("hero_image").exclude(
        hero_image__isnull=True
    ):
        image_title = page.hero_image.title[:100]
        page.hero_image_alt_text = image_title
        page.save(update_fields=["hero_image_alt_text"])


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0028_migrate_image_block_values_to_new_block_structure"),
    ]

    operations = [migrations.RunPython(move_alt_text, migrations.RunPython.noop)]
