# Generated by Django 3.2.13 on 2022-05-11 14:16

from django.db import migrations, models
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0039_alter_insightspage_body"),
    ]

    operations = [
        migrations.AddField(
            model_name="insightspage",
            name="custom_warning_text",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="If specified, will be used for the content warning. Otherwise the default text will be used.",
                verbose_name="custom content warning text (optional)",
            ),
        ),
        migrations.AddField(
            model_name="insightspage",
            name="display_content_warning",
            field=models.BooleanField(
                default=False, verbose_name="display a content warning on this page"
            ),
        ),
    ]
