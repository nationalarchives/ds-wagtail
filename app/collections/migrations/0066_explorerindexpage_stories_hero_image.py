# Generated by Django 5.2.4 on 2025-07-29 08:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collections', '0065_explorerindexpage_hero_image_and_more'),
        ('images', '0013_alter_customimage_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='explorerindexpage',
            name='stories_hero_image',
            field=models.ForeignKey(blank=True, help_text='The stories section hero image to display on the Explorer Index Page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.customimage', verbose_name='hero image'),
        ),
    ]
