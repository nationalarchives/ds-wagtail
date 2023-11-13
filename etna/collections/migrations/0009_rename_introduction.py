# Generated by Django 3.1.8 on 2021-07-09 14:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("collections", "0008_topicexplorerpage_body"),
    ]

    operations = [
        migrations.RenameField(
            model_name="explorerindexpage",
            old_name="introduction",
            new_name="sub_heading",
        ),
        migrations.RenameField(
            model_name="timeperiodexplorerpage",
            old_name="introduction",
            new_name="sub_heading",
        ),
        migrations.RenameField(
            model_name="topicexplorerpage",
            old_name="introduction",
            new_name="sub_heading",
        ),
        migrations.AddField(
            model_name="resultspage",
            name="sub_heading",
            field=models.CharField(default="", max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="resultspage",
            name="introduction",
            field=models.TextField(),
        ),
    ]