from django.db import migrations
from datetime import datetime


def migrate_forwards(apps, schema_editor):
    RecordArticlePage = apps.get_model("articles", "RecordArticlePage")

    for page in RecordArticlePage.objects.all():
        for block in page.promoted_links:
            if block.value["promoted_items"]:
                for item in block.value["promoted_items"]:
                    if item["publication_date"]:
                        date_obj = datetime.strptime(
                            item["publication_date"], "%Y-%m-%d"
                        ).date()
                        formatted_date = date_obj.strftime("%d %B %Y")
                        item["publication_date"] = formatted_date
        page.save()


def migrate_backwards(apps, schema_editor):
    RecordArticlePage = apps.get_model("articles", "RecordArticlePage")

    for page in RecordArticlePage.objects.all():
        for block in page.promoted_links:
            if block.value["promoted_items"]:
                for item in block.value["promoted_items"]:
                    if isinstance(item["publication_date"], datetime):
                        continue
                    date_obj = datetime.strptime(item["publication_date"], "%d %B %Y")
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    print(formatted_date)
                    item["publication_date"] = formatted_date
        page.save()


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0089_alter_articleindexpage_featured_article"),
    ]

    operations = [
        migrations.RunPython(migrate_forwards, migrate_backwards),
    ]
