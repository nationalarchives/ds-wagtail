# Generated by Django 5.0.8 on 2024-08-08 11:44
# etna:allowAlterField

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0009_alter_customimage_custom_sensitive_image_warning"),
        ("people", "0006_alter_authortag_author"),
    ]

    operations = [
        migrations.AddField(
            model_name="peopleindexpage",
            name="twitter_og_description",
            field=models.TextField(
                blank=True,
                help_text="If left blank, the OpenGraph description will be used.",
                null=True,
                verbose_name="Twitter OpenGraph description",
            ),
        ),
        migrations.AddField(
            model_name="peopleindexpage",
            name="twitter_og_image",
            field=models.ForeignKey(
                blank=True,
                help_text="If left blank, the OpenGraph image will be used.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.customimage",
                verbose_name="Twitter OpenGraph image",
            ),
        ),
        migrations.AddField(
            model_name="peopleindexpage",
            name="twitter_og_title",
            field=models.CharField(
                blank=True,
                help_text="If left blank, the OpenGraph title will be used.",
                max_length=255,
                null=True,
                verbose_name="Twitter OpenGraph title",
            ),
        ),
        migrations.AddField(
            model_name="personpage",
            name="twitter_og_description",
            field=models.TextField(
                blank=True,
                help_text="If left blank, the OpenGraph description will be used.",
                null=True,
                verbose_name="Twitter OpenGraph description",
            ),
        ),
        migrations.AddField(
            model_name="personpage",
            name="twitter_og_image",
            field=models.ForeignKey(
                blank=True,
                help_text="If left blank, the OpenGraph image will be used.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.customimage",
                verbose_name="Twitter OpenGraph image",
            ),
        ),
        migrations.AddField(
            model_name="personpage",
            name="twitter_og_title",
            field=models.CharField(
                blank=True,
                help_text="If left blank, the OpenGraph title will be used.",
                max_length=255,
                null=True,
                verbose_name="Twitter OpenGraph title",
            ),
        ),
        migrations.AlterField(
            model_name="peopleindexpage",
            name="search_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Image that will appear when this page is shared on social media. This will default to the teaser image if left blank.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.customimage",
                verbose_name="OpenGraph image",
            ),
        ),
        migrations.AlterField(
            model_name="personpage",
            name="search_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Image that will appear when this page is shared on social media. This will default to the teaser image if left blank.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.customimage",
                verbose_name="OpenGraph image",
            ),
        ),
    ]
