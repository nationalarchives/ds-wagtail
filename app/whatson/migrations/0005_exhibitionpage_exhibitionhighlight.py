# Generated by Django 4.2.7 on 2023-11-22 14:39

from django.db import migrations, models
import django.db.models.deletion
import app.collections.models
import app.core.blocks.page_list
import modelcluster.contrib.taggit
import modelcluster.fields
import uuid
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("articles", "0099_alter_articleindexpage_featured_article_and_more"),
        ("images", "0008_alter_customimagerendition_file"),
        ("whatson", "0004_eventsession_session_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExhibitionPage",
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
                    "subtitle",
                    models.CharField(
                        blank=True,
                        help_text="A subtitle for the event.",
                        max_length=255,
                        verbose_name="subtitle",
                    ),
                ),
                (
                    "hero_text_colour",
                    models.CharField(
                        choices=[("light", "Light"), ("dark", "Dark")],
                        help_text="The colour of the text in the hero image.",
                        max_length=255,
                        verbose_name="hero text colour",
                    ),
                ),
                (
                    "start_date",
                    models.DateTimeField(null=True, verbose_name="start date"),
                ),
                ("end_date", models.DateTimeField(null=True, verbose_name="end date")),
                (
                    "min_price",
                    models.IntegerField(default=0, verbose_name="minimum price"),
                ),
                (
                    "max_price",
                    models.IntegerField(default=0, verbose_name="maximum price"),
                ),
                (
                    "dwell_time",
                    models.CharField(
                        blank=True,
                        help_text="The average dwell time for the exhibition.",
                        max_length=255,
                        verbose_name="dwell time",
                    ),
                ),
                (
                    "target_audience",
                    models.CharField(
                        blank=True,
                        help_text="The target audience for the exhibition.",
                        max_length=255,
                        verbose_name="target audience",
                    ),
                ),
                (
                    "location",
                    models.CharField(
                        help_text="The location of the exhibition venue.",
                        max_length=255,
                        verbose_name="location",
                    ),
                ),
                (
                    "location_url",
                    models.URLField(
                        blank=True,
                        help_text="The URL of the exhibition venue.",
                        verbose_name="location url",
                    ),
                ),
                (
                    "description",
                    wagtail.fields.RichTextField(
                        help_text="A description of the exhibition.",
                        verbose_name="description",
                    ),
                ),
                (
                    "need_to_know",
                    wagtail.fields.RichTextField(
                        blank=True,
                        help_text="Useful information about the exhibition.",
                        verbose_name="need to know",
                    ),
                ),
                (
                    "need_to_know_cta",
                    models.CharField(
                        blank=True,
                        help_text="The call to action text for the need to know section.",
                        max_length=255,
                        verbose_name="need to know CTA",
                    ),
                ),
                (
                    "need_to_know_url",
                    models.URLField(
                        blank=True,
                        help_text="The URL for the need to know section.",
                        verbose_name="need to know URL",
                    ),
                ),
                (
                    "articles_title",
                    models.CharField(
                        blank=True,
                        help_text="The title to display for the articles section.",
                        max_length=255,
                    ),
                ),
                (
                    "related_articles",
                    wagtail.fields.StreamField(
                        [
                            (
                                "relatedarticles",
                                wagtail.blocks.StreamBlock(
                                    [
                                        (
                                            "pages",
                                            app.core.blocks.page_list.PageListBlock(
                                                "articles.ArticlePage",
                                                "articles.RecordArticlePage",
                                                "articles.FocusedArticlePage",
                                            ),
                                        )
                                    ]
                                ),
                            )
                        ],
                        blank=True,
                        null=True,
                        use_json_field=True,
                    ),
                ),
                (
                    "short_title",
                    models.CharField(
                        blank=True,
                        help_text="A short title for the event. This will be used in the event listings.",
                        max_length=50,
                        verbose_name="short title",
                    ),
                ),
                (
                    "hero_image",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.customimage",
                    ),
                ),
                (
                    "need_to_know_image",
                    models.ForeignKey(
                        blank=True,
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
                "verbose_name": "exhibition page",
            },
            bases=(
                app.collections.models.TopicalPageMixin,
                "wagtailcore.page",
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="ExhibitionHighlight",
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
                ("title", models.CharField(max_length=255, verbose_name="title")),
                (
                    "image",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.customimage",
                    ),
                ),
                (
                    "link",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="highlights",
                        to="whatson.exhibitionpage",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
