# Generated by Django 5.1.5 on 2025-02-10 08:55
# etna:allowAlterField
# etna:allowRemoveField

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collections', '0061_explorerindexpage_short_title_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='highlightgallerypage',
            name='display_content_warning',
        ),
        migrations.AlterField(
            model_name='highlightgallerypage',
            name='custom_warning_text',
            field=wagtail.fields.RichTextField(blank=True, help_text='If specified, will be used for the content warning.', verbose_name='custom content warning text (optional)'),
        ),
    ]
