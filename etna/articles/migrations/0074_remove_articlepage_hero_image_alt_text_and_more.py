# Generated by Django 4.1.8 on 2023-04-12 09:54

from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0073_recordarticlepage_featured_highlight_gallery"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="articlepage",
            name="hero_image_alt_text",
        ),
        migrations.RemoveField(
            model_name="articlepage",
            name="hero_image_decorative",
        ),
        migrations.AlterField(
            model_name="articlepage",
            name="hero_image_caption",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="An optional caption for hero images. This could be used for image sources or for other useful metadata.",
                verbose_name="hero image caption (optional)",
            ),
        ),
    ]
