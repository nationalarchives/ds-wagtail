# Generated by Django 4.0.8 on 2023-02-02 11:03

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0050_swap_image_reference_fields_to_new_model"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pagegalleryimage",
            name="is_sensitive",
        ),
        migrations.RemoveField(
            model_name="pagegalleryimage",
            name="transcription_text",
        ),
        migrations.RemoveField(
            model_name="pagegalleryimage",
            name="translation_text",
        ),
    ]