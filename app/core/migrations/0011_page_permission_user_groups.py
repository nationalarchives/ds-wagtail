from django.db import migrations


def create_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    # Attach these permissions to the Wagtail Page model so they can be
    # granted on a per-page basis. We obtain the content type via get_for_model(Page).
    try:
        from wagtail.models import Page
        page_ct = ContentType.objects.get_for_model(Page)
    except (ContentType.DoesNotExist, ImportError, AttributeError):
        return

    perms = [
        {"codename": "can_delete_pages", "name": "Can delete pages (per-page toggle)"},
        {"codename": "can_unpublish_pages", "name": "Can unpublish pages (per-page toggle)"},
    ]

    for p in perms:
        Permission.objects.get_or_create(content_type=page_ct, codename=p["codename"], defaults={"name": p["name"]})


def remove_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Permission.objects.filter(codename__in=["can_delete_pages", "can_unpublish_pages"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_partnerlogo"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(create_permissions, reverse_code=remove_permissions),
    ]
