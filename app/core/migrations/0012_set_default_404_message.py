# Manually created on 2026-01-15

from django.db import migrations


def set_default_404_message(apps, schema_editor):
    """
    Set the 404 error message for the default site.
    """
    Site = apps.get_model("wagtailcore", "Site")
    ErrorPageSettings = apps.get_model("core", "ErrorPageSettings")

    try:
        default_site = Site.objects.get(is_default_site=True)

        _, _ = ErrorPageSettings.objects.get_or_create(
            site=default_site,
            defaults={
                "title": "Page not found",
                "message": (
                    "<p>If you typed the web address, check it is correct.</p>"
                    "<p>If you pasted the web address, check you copied the entire address.</p>"
                    "<p>If the web address is correct or you selected a link or button, "
                    "<a href='https://www.nationalarchives.gov.uk/contact-us/'>contact us</a> "
                    "us to let us help.</p>"
                ),
            },
        )

    except Site.DoesNotExist:
        pass


def reverse_set_default_404_message(apps, schema_editor):
    """
    Reverse the migration by clearing the 404 message.
    """
    Site = apps.get_model("wagtailcore", "Site")
    ErrorPageSettings = apps.get_model("core", "ErrorPageSettings")

    try:
        default_site = Site.objects.get(is_default_site=True)
        ErrorPageSettings.objects.filter(site=default_site).delete()
    except Site.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_errorpagesettings"),
        ("wagtailcore", "0096_referenceindex_referenceindex_source_object_and_more"),
    ]

    operations = [
        migrations.RunPython(
            set_default_404_message,
            reverse_set_default_404_message,
        ),
    ]
