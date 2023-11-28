# Generated by Django 4.2.5 on 2023-10-02 14:35

from django.db import migrations, models
import django.db.models.deletion
import etna.analytics.mixins
import etna.collections.models
import modelcluster.contrib.taggit
import modelcluster.fields
import uuid
import wagtail.fields
import wagtailmetadata.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("articles", "0097_alter_articlepage_mark_new_on_next_publish_and_more"),
        ("images", "0008_alter_customimagerendition_file"),
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccessType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="name")),
                (
                    "slug",
                    models.SlugField(max_length=255, unique=True, verbose_name="slug"),
                ),
            ],
            options={
                "verbose_name": "Access type",
                "verbose_name_plural": "Access types",
            },
        ),
        migrations.CreateModel(
            name="AudienceType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="name")),
                (
                    "slug",
                    models.SlugField(max_length=255, unique=True, verbose_name="slug"),
                ),
            ],
            options={
                "verbose_name": "Audience type",
                "verbose_name_plural": "Audience types",
            },
        ),
        migrations.CreateModel(
            name="EventType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="name")),
                (
                    "slug",
                    models.SlugField(max_length=255, unique=True, verbose_name="slug"),
                ),
            ],
            options={
                "verbose_name": "event type",
                "verbose_name_plural": "event types",
            },
        ),
        migrations.CreateModel(
            name="WhatsOnPage",
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
                    "intro",
                    wagtail.fields.RichTextField(
                        help_text="1-2 sentences introducing the subject of the page, and explaining why a user should read on.",
                        max_length=300,
                        verbose_name="introductory text",
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
                "verbose_name": "What's On page",
            },
            bases=(
                wagtailmetadata.models.WagtailImageMetadataMixin,
                etna.analytics.mixins.DataLayerMixin,
                "wagtailcore.page",
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="EventSpeaker",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                ("name", models.CharField(max_length=100, verbose_name="name")),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="description"
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.customimage",
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="speakers",
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="EventSession",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start", models.DateTimeField(verbose_name="starts at")),
                ("end", models.DateTimeField(verbose_name="ends at")),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sessions",
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={
                "verbose_name": "session",
                "verbose_name_plural": "sessions",
                "ordering": ["start"],
            },
        ),
        migrations.CreateModel(
            name="EventPage",
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
                    "intro",
                    wagtail.fields.RichTextField(
                        help_text="1-2 sentences introducing the subject of the page, and explaining why a user should read on.",
                        max_length=300,
                        verbose_name="introductory text",
                    ),
                ),
                ("article_tag_names", models.TextField(editable=False, null=True)),
                (
                    "start_date",
                    models.DateTimeField(
                        editable=False, null=True, verbose_name="start date"
                    ),
                ),
                (
                    "end_date",
                    models.DateTimeField(
                        editable=False, null=True, verbose_name="end date"
                    ),
                ),
                (
                    "description",
                    wagtail.fields.RichTextField(
                        blank=True,
                        help_text="A description of the event.",
                        verbose_name="description",
                    ),
                ),
                (
                    "useful_info",
                    wagtail.fields.RichTextField(
                        blank=True,
                        help_text="Useful information about the event.",
                        verbose_name="need to know",
                    ),
                ),
                (
                    "target_audience",
                    wagtail.fields.RichTextField(
                        blank=True,
                        help_text="Info about the target audience for the event.",
                        verbose_name="who it's for",
                    ),
                ),
                (
                    "venue_type",
                    models.CharField(
                        choices=[
                            ("online", "Online"),
                            ("in_person", "In person"),
                            ("hybrid", "Hybrid"),
                        ],
                        default="in_person",
                        max_length=15,
                        verbose_name="venue type",
                    ),
                ),
                (
                    "venue_website",
                    models.URLField(
                        blank=True,
                        help_text="The website for the venue.",
                        max_length=255,
                        verbose_name="venue website",
                    ),
                ),
                (
                    "venue_address",
                    wagtail.fields.RichTextField(
                        blank=True,
                        help_text="The address of the venue.",
                        verbose_name="venue address",
                    ),
                ),
                (
                    "venue_space_name",
                    models.CharField(
                        blank=True,
                        help_text="The name of the venue space.",
                        max_length=255,
                        verbose_name="venue space name",
                    ),
                ),
                (
                    "video_conference_info",
                    wagtail.fields.RichTextField(
                        blank=True,
                        help_text="Useful information about the video conference.",
                        verbose_name="video conference info",
                    ),
                ),
                (
                    "registration_url",
                    models.URLField(
                        editable=False, max_length=255, verbose_name="registration url"
                    ),
                ),
                (
                    "registration_cost",
                    models.IntegerField(
                        editable=False, null=True, verbose_name="registration cost"
                    ),
                ),
                (
                    "registration_info",
                    wagtail.fields.RichTextField(
                        blank=True,
                        help_text="Additional information about how to register for the event.",
                        verbose_name="registration info",
                    ),
                ),
                (
                    "contact_info",
                    wagtail.fields.RichTextField(
                        blank=True,
                        help_text="Information about who to contact regarding the event.",
                        verbose_name="contact info",
                    ),
                ),
                (
                    "short_title",
                    models.CharField(
                        help_text="A short title for the event. This will be used in the event listings.",
                        max_length=50,
                        verbose_name="short title",
                    ),
                ),
                (
                    "event_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="whatson.eventtype",
                    ),
                ),
                (
                    "lead_image",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.customimage",
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
                    "tags",
                    modelcluster.contrib.taggit.ClusterTaggableManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="articles.TaggedArticle",
                        to="articles.ArticleTag",
                        verbose_name="Tags",
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
                "verbose_name": "event page",
            },
            bases=(
                etna.collections.models.TopicalPageMixin,
                wagtailmetadata.models.WagtailImageMetadataMixin,
                etna.analytics.mixins.DataLayerMixin,
                "wagtailcore.page",
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="EventHost",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                ("name", models.CharField(max_length=100, verbose_name="name")),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="description"
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.customimage",
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hosts",
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="EventAudienceType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "audience_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_audience_types",
                        to="whatson.audiencetype",
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_audience_types",
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="EventAccessType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "access_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_access_types",
                        to="whatson.accesstype",
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_access_types",
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]