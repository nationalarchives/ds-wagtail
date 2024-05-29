# Generated by Django 3.1.8 on 2021-07-08 07:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailimages", "0023_add_choose_permissions"),
        ("collections", "0005_resultspagerecordpage"),
    ]

    operations = [
        migrations.AddField(
            model_name="resultspagerecordpage",
            name="teaser_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AlterField(
            model_name="resultspagerecordpage",
            name="record_iaid",
            field=models.TextField(verbose_name="Record"),
        ),
    ]