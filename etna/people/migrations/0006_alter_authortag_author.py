# Generated by Django 5.0.7 on 2024-08-06 07:20
# etna:allowAlterField

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0005_rename_authorindexpage_peopleindexpage_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="authortag",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="people_pages",
                to="people.personpage",
                verbose_name="author",
            ),
        ),
    ]
