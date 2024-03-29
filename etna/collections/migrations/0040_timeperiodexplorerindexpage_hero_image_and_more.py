# Generated by Django 4.1.7 on 2023-04-05 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("images", "0006_remove_customimage_transcription_language_and_more"),
        ("collections", "0039_remove_highlight_long_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="timeperiodexplorerindexpage",
            name="hero_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.customimage",
            ),
        ),
        migrations.AddField(
            model_name="topicexplorerindexpage",
            name="hero_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.customimage",
            ),
        ),
    ]
