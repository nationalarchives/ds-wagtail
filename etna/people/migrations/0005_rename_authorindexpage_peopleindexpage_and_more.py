# Generated by Django 5.0.7 on 2024-08-01 11:21
# etna:allowRenameModel

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("alerts", "0003_alert_name_alter_alert_title"),
        ("images", "0009_alter_customimage_custom_sensitive_image_warning"),
        ("people", "0004_alter_personpage_options"),
        ("wagtailcore", "0093_uploadedfile"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AuthorIndexPage",
            new_name="PeopleIndexPage",
        ),
        migrations.RenameModel(
            old_name="AuthorPage",
            new_name="PersonPage",
        ),
    ]