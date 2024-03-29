# Generated by Django 4.1.7 on 2023-04-06 09:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("images", "0006_remove_customimage_transcription_language_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customimage",
            name="custom_sensitive_image_warning",
            field=models.TextField(
                blank=True,
                help_text='Replaces the default warning message where the image is displayed. For example: "This image has been marked as potentially sensitive because it contains depictions of violence".',
                max_length=200,
                verbose_name="Why might this image be considered sensitive? (optional)",
            ),
        ),
        migrations.AlterField(
            model_name="customimage",
            name="is_sensitive",
            field=models.BooleanField(
                default=False,
                help_text="Tick this if the image contains content which some people may find offensive or distressing. For example, photographs of violence or injury detail.",
                verbose_name="This image is considered sensitive",
            ),
        ),
    ]
