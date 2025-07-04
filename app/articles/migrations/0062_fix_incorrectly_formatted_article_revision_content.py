from django.db import migrations


def migrate_forwards(apps, schema_editor):
    ArticlePage = apps.get_model("articles", "ArticlePage")
    for page in (
        ArticlePage.objects.all()
        .select_related("latest_revision")
        .prefetch_related("page_topics", "page_time_periods")
    ):
        rev = page.latest_revision
        rev.content["page_time_periods"] = [
            {"pk": obj.pk, "time_period": obj.time_period_id}
            for obj in page.page_time_periods.all()
        ]
        rev.content["page_topics"] = [
            {"pk": obj.pk, "topic": obj.topic_id} for obj in page.page_topics.all()
        ]
        rev.save(update_fields=["content"])


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0061_remove_articlepage_time_period_and_topic"),
    ]

    operations = [
        migrations.RunPython(migrate_forwards, migrations.RunPython.noop),
    ]
