# Generated by Django 4.1.7 on 2023-03-23 11:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("collections", "0038_highlightgallerypage_custom_warning_text_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="highlight",
            name="long_description",
        ),
    ]
