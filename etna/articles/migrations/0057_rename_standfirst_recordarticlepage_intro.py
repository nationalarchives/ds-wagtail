# Generated by Django 4.0.8 on 2023-02-22 11:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0056_set_teaser_text_from_intro"),
    ]

    operations = [
        migrations.RenameField(
            model_name="recordarticlepage",
            old_name="standfirst",
            new_name="intro",
        ),
    ]
