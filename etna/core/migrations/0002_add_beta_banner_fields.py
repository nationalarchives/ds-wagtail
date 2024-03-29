# Generated by Django 3.2.13 on 2022-06-13 08:09

from django.db import migrations, models
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="beta_banner_link",
            field=models.CharField(blank=True, max_length=200, verbose_name="link to"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="beta_banner_link_text",
            field=models.CharField(
                default="Find out more", max_length=200, verbose_name="link text"
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="beta_banner_standfirst",
            field=models.CharField(
                default="What does the 'beta' label mean?",
                max_length=200,
                verbose_name="standfirst",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="beta_banner_text",
            field=wagtail.fields.RichTextField(
                default="<p>This beta site contains new services and features currently in development. Many of these features are works in progress and are being updated regularly. You can help us improve them by providing feedback as you use the site.</p> ",
                verbose_name="text",
            ),
        ),
    ]
