# Generated by Django 5.0.6 on 2024-07-02 08:55

import django.db.models.deletion
import etna.analytics.mixins
import uuid
import wagtail_headless_preview.models
import wagtailmetadata.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("generic_pages", "0013_alter_generalpage_body"),
        ("images", "0008_alter_customimagerendition_file"),
        ("wagtailcore", "0093_uploadedfile"),
    ]

    operations = [
        migrations.CreateModel(
            name="HubPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "teaser_text",
                    models.TextField(
                        help_text="A short, enticing description of this page. This will appear in promos and under thumbnails around the site.",
                        max_length=160,
                        verbose_name="teaser text",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        unique=True,
                        verbose_name="UUID",
                    ),
                ),
                (
                    "search_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.customimage",
                        verbose_name="Search image",
                    ),
                ),
                (
                    "teaser_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Image that will appear on thumbnails and promos around the site.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.customimage",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(
                wagtailmetadata.models.WagtailImageMetadataMixin,
                etna.analytics.mixins.DataLayerMixin,
                wagtail_headless_preview.models.HeadlessPreviewMixin,
                "wagtailcore.page",
                models.Model,
            ),
        ),
    ]