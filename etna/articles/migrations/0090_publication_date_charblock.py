from django.db import migrations
from datetime import datetime


def migrate_forwards(apps, schema_editor):
    RecordArticlePage = apps.get_model("articles", "RecordArticlePage")

    for page in RecordArticlePage.objects.all():
        for block in page.promoted_links:
            if block.value["promoted_items"]:
                for item in block.value["promoted_items"]:
                    item["publication_date"] = datetime.strptime(item["publication_date"], "%Y-%m-%d").date().strftime("%d %B %Y")
        page.save()

    ArticlePage = apps.get_model("articles", "ArticlePage")

    for page in ArticlePage.objects.all():
        for section in page.body:
            if section.block_type == "content_section":
                for block in section.value["content"]:
                    if block.block_type == "promoted_item" and block.value["publication_date"]:
                        block.value["publication_date"] = datetime.strptime(str(block.value["publication_date"]), "%Y-%m-%d").date().strftime("%d %B %Y")
        page.save()


def migrate_backwards(apps, schema_editor):
    RecordArticlePage = apps.get_model("articles", "RecordArticlePage")

    for page in RecordArticlePage.objects.all():
        for block in page.promoted_links:
            if block.value["promoted_items"]:
                for item in block.value["promoted_items"]:
                    item["publication_date"] = datetime.strptime(item["publication_date"], "%d %B %Y").strftime("%Y-%m-%d")
        page.save()

    # ArticlePage = apps.get_model("articles", "ArticlePage")

    # for page in ArticlePage.objects.all():
    #     for section in page.body:
    #         if section.block_type == "content_section":
    #             for block in section.value["content"]:
    #                 if block.block_type == "promoted_item":
    #                     for item in block.value:
    #                         if item == "publication_date":
    #                             # item["publication_date"] = datetime.strptime(item["publication_date"], "%d %B %Y").strftime("%Y-%m-%d")
    #                             print("BEFORE FORMAT:", item.value)
                        # block.value["publication_date"] = datetime.strptime(block.value["publication_date"], "%d %B %Y").strftime("%Y-%m-%d")
                        # print("AFTER FORMAT:",block.value["publication_date"])
        page.save()


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0089_alter_articleindexpage_featured_article"),
    ]

    operations = [
        migrations.RunPython(migrate_forwards, migrate_backwards),
    ]
