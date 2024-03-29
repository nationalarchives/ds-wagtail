# Generated by Django 4.2.1 on 2023-06-21 19:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0006_add_comment_prompt_text_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedbacksubmission",
            name="comment_prompt_text",
            field=models.CharField(
                default="", max_length=200, verbose_name="comment prompt text"
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="feedbacksubmission",
            name="comment",
            field=models.TextField(verbose_name="comment"),
        ),
    ]
