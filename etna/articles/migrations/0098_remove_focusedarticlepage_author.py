# Generated by Django 4.2.4 on 2023-08-15 11:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0097_alter_articlepage_mark_new_on_next_publish_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="focusedarticlepage",
            name="author",
        ),
    ]