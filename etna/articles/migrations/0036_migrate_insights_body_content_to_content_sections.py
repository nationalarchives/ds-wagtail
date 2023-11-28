# Generated by Django 3.2.12 on 2022-04-05 20:17
import json

from django.db import migrations


def migrate_forwards(apps, schema_editor):
    InsightsPage = apps.get_model("articles", "InsightsPage")
    Revision = apps.get_model("wagtailcore", "Revision")
    for page in InsightsPage.objects.only("id", "title", "body").iterator():
        new_content = []
        current_section_heading = None
        current_section_content = []
        current_sub_section_heading = None
        current_sub_section_content = []
        current_content_level = 1

        def close_current_sub_section():
            if current_sub_section_content or current_sub_section_heading:
                current_section_content.append(
                    {
                        "type": "content_sub_section",
                        "value": {
                            "heading": current_sub_section_heading or "",
                            "content": list(current_sub_section_content),
                        },
                    }
                )
                current_sub_section_content.clear()

        def close_current_section():
            if current_section_content or current_section_heading:
                close_current_sub_section()
                new_content.append(
                    {
                        "type": "content_section",
                        "value": {
                            "heading": current_section_heading,
                            "content": list(current_section_content),
                        },
                    }
                )
                current_section_content.clear()

        for block in page.body._raw_data:
            if (
                block["type"] == "section"
                or block["type"] == "paragraph_with_heading"
                and block["value"]["heading_level"] == "h2"
            ):
                close_current_section()
                current_content_level = 1
                current_section_heading = block["value"]["heading"]

            if (
                block["type"] == "paragraph_with_heading"
                and block["value"]["heading_level"] == "h3"
            ):
                close_current_sub_section()
                current_content_level = 2
                current_sub_section_heading = block["value"]["heading"]

            if (
                block["type"] == "paragraph_with_heading"
                and block["value"]["heading_level"] == "h4"
            ):
                current_sub_section_content.append(
                    {
                        "type": "sub_heading",
                        "value": {
                            "heading": block["value"]["heading"],
                        },
                    }
                )

            if block["type"] == "paragraph_with_heading":
                # Add the 'paragraph' content as a separate 'paragraph' block
                paragraph_block = {
                    "type": "paragraph",
                    "value": {
                        "text": block["value"]["paragraph"],
                    },
                }
                if current_content_level == 2:
                    current_sub_section_content.append(paragraph_block)
                else:
                    current_section_content.append(paragraph_block)

            elif block["type"] != "section":
                # All other blocks can be added to the section as-is
                if current_content_level == 2:
                    current_sub_section_content.append(block)
                else:
                    current_section_content.append(block)

        # Close the final section if there is content outstanding
        close_current_section()

        # Update the streamfield value and save the changes
        page.body = json.dumps(new_content)
        page.save(update_fields=["body"])

        # Update the page's latest revision, so that changes 'stick' in the editor
        latest_revision = (
            Revision.objects.filter(page_id=page.id).order_by("-created_at").first()
        )
        if latest_revision:
            revision_content = json.loads(latest_revision.content_json)
            revision_content["body"] = new_content
            latest_revision.content_json = json.dumps(revision_content)


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0077_alter_revision_user"),
        ("articles", "0035_add_content_section_blocks_to_insights_body"),
    ]

    # NOTE: This data migration can only work one way, because new content
    # options allow for layouts that aren't possible to represent with the
    # block optons available before '0035_alter_insightspage_body'
    operations = [migrations.RunPython(migrate_forwards, migrations.RunPython.noop)]