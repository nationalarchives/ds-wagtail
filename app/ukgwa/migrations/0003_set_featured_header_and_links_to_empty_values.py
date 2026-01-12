# Manually created on 2026-01-12 14:05

from django.db import migrations


def populate_defaults_on_reverse(apps, schema_editor):
    """
    Populate default values for the featured_links_heading and featured_links fields.
    This prevents integrity errors when reverting to the old schema.
    """
    UKGWAHomePage = apps.get_model("ukgwa", "UKGWAHomePage")

    for page in UKGWAHomePage.objects.all():
        page.featured_links_heading = ""
        page.featured_links = "[]"
        page.save(update_fields=["featured_links_heading", "featured_links"])


class Migration(migrations.Migration):

    dependencies = [
        ("ukgwa", "0002_alter_ukgwahomepage_featured_links_and_more"),
    ]

        
    operations = [
        migrations.RunPython(
            migrations.RunPython.noop, 
            reverse_code=populate_defaults_on_reverse
        ),
    ]
