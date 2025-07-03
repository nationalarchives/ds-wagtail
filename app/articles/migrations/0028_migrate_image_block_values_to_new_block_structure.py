import json

from django.db import migrations


def update_structblock_value(current_value, forwards=True):
    if forwards:
        # If running forwards, we want to add 'image' StructBlock values
        # from 'teaser_image' and 'teaser_alt_text' values
        current_value["image"] = {
            "image": current_value.get("teaser_image", None),
            "decorative": True,
            "alt_text": current_value.get("teaser_alt_text", ""),
            "caption": "",
        }
    else:
        # If running backwards, we want to set 'teaser_image' and 'teaser_alt_text'
        # values from the 'image' StructBlock value.
        if image_dict := current_value.pop("image"):
            current_value["teaser_image"] = image_dict.get("image")
            current_value["teaser_alt_text"] = image_dict.get("alt_text", "")


def update_body_values(apps, schema_editor, forwards=True):
    InsightsPage = apps.get_model("articles", "InsightsPage")

    for obj in InsightsPage.objects.only("id", "body").iterator():
        page_updated = False

        for block in obj.body._raw_data:
            # NOTE: We're updating the '_raw_data' attribute directly here
            if block["type"] in ("promoted_item", "featured_record"):
                # Update image-related values to match the target structure
                update_structblock_value(block["value"], forwards)
                page_updated = True

        if page_updated:
            # StreamField expects values to be a string or a StreamValue, so let's
            # convert our dict value to a string
            new_value = json.dumps(obj.body._raw_data)
            # Update the streamfield value and save the changes
            obj.body = new_value
            obj.save(update_fields=["body"])


def migrate_forwards(apps, schema_editor):
    update_body_values(apps, schema_editor, forwards=True)


def migrate_backwards(apps, schema_editor):
    update_body_values(apps, schema_editor, forwards=False)


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0027_change_accessible_image_required"),
    ]

    operations = [migrations.RunPython(migrate_forwards, migrate_backwards)]
