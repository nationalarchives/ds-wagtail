from typing import Any, Dict, List, Tuple, Union

from django.db import models
from django.http import HttpRequest
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from rest_framework import serializers
from taggit.models import ItemBase, TagBase

from etna.core.models import (
    BasePageWithIntro,
    ContentWarningMixin,
    HeroImageMixin,
    NewLabelMixin,
)
from etna.core.utils import skos_id_from_text

from .blocks import ArticlePageStreamBlock


@register_snippet
class ArticleTag(TagBase):
    free_tagging = False
    skos_id = models.CharField(
        blank=True,
        unique=True,
        db_index=True,
        max_length=100,
        verbose_name="SKOS identifier",
        help_text="Used as the identifier for this tag when sending page metatdata to the CIIM API.",
    )

    class Meta:
        verbose_name = "article tag"
        verbose_name_plural = "article tags"

    panels = (
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("skos_id"),
    )

    def clean(self, *args, **kwargs):
        if not self.skos_id and self.name:
            # Generate a unique skos_id value for new tags
            base_value = skos_id_from_text(self.name)
            self.skos_id = base_value
            i = 2
            while (
                ArticleTag.objects.exclude(id=self.id)
                .filter(skos_id=self.skos_id)
                .exists()
            ):
                self.skos_id = f"{base_value[:97]}_{i}"
                i += 1
        return super().clean(*args, **kwargs)


class TaggedArticle(ItemBase):
    tag = models.ForeignKey(
        ArticleTag, related_name="tagged_article", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


class ArticleTagMixin(models.Model):
    """Mixin to add article tags to a Page."""

    article_tag_names = models.TextField(editable=False, null=True)
    tags = ClusterTaggableManager(through=TaggedArticle, blank=True)

    class Meta:
        abstract = True

    promote_panels = [
        FieldPanel("tags"),
    ]

    search_fields = [
        index.SearchField("article_tag_names", boost=2),
    ]

    api_fields = [APIField("tags")]


# TODO: Make better
class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = (
            "id",
            "title",
            "url_path",
        )


class ArticlePage(
    HeroImageMixin,
    ContentWarningMixin,
    NewLabelMixin,
    ArticleTagMixin,
    BasePageWithIntro,
):
    """ArticlePage

    The ArticlePage model.
    """

    body = StreamField(ArticlePageStreamBlock, blank=True, null=True)

    # DataLayerMixin overrides
    gtm_content_group = "Explore the collection"

    template = "articles/article_page.html"

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")
        verbose_name_public = _("the story of")

    content_panels = (
        BasePageWithIntro.content_panels
        + HeroImageMixin.content_panels
        + [
            MultiFieldPanel(
                [
                    FieldPanel("display_content_warning"),
                    FieldPanel("custom_warning_text"),
                ],
                heading="Content Warning Options",
                classname="collapsible",
            ),
            FieldPanel("body"),
        ]
    )

    promote_panels = (
        NewLabelMixin.promote_panels
        + BasePageWithIntro.promote_panels
        + ArticleTagMixin.promote_panels
    )

    subpage_types = []

    search_fields = (
        BasePageWithIntro.search_fields
        + ArticleTagMixin.search_fields
        + [
            index.SearchField("body"),
        ]
    )

    api_fields = (
        BasePageWithIntro.api_fields
        + HeroImageMixin.api_fields
        + ContentWarningMixin.api_fields
        + NewLabelMixin.api_fields
        + ArticleTagMixin.api_fields
        + [
            APIField("similar_items", serializer=PageSerializer(many=True)),
            APIField("latest_items", serializer=PageSerializer(many=True)),
            APIField("body"),
        ]
    )

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        data = super().get_datalayer_data(request)
        data.update(
            customDimension4="; ".join(obj.title for obj in self.topics),
            customDimension6="; ".join(self.article_tag_names.split("\n")),
            customDimension7="; ".join(obj.title for obj in self.time_periods),
        )
        return data

    def save(self, *args, **kwargs):
        """
        Overrides Page.save() to ensure 'article_tag_names' always reflects the tags() value
        """
        if (
            "update_fields" not in kwargs
            or "article_tag_names" in kwargs["update_fields"]
        ):
            self.article_tag_names = "\n".join(t.name for t in self.tags.all())
        super().save(*args, **kwargs)

    @cached_property
    def similar_items(
        self,
    ) -> Tuple[Union["ArticlePage"], ...]:
        """
        Returns a maximum of three ArticlePages that are tagged with at least
        one of the same ArticleTags. Items should be ordered by the number
        of tags they have in common.
        """
        if not self.article_tag_names:
            # Avoid unncecssary lookups
            return ()

        tag_ids = self.tagged_items.values_list("tag_id", flat=True)
        if not tag_ids:
            # Avoid unncecssary lookups
            return ()

        # Identify other live pages with tags in common
        related_tags = (
            Page.objects.filter(tagged_items__tag_id__in=tag_ids)
            .exact_type(ArticlePage)
            .live()
            .public()
            .not_page(self)
        )

        return tuple(
            Page.objects.filter(id__in=related_tags).order_by("-first_published_at")[:3]
        )

    @cached_property
    def latest_items(
        self,
    ) -> List[Union["ArticlePage"]]:
        """
        Return the three most recently published ArticlePages,
        excluding this object.
        """

        latest_query_set = []

        for page_type in [ArticlePage]:
            latest_query_set.extend(
                page_type.objects.live()
                .public()
                .exclude(id__in=[page.id for page in self.similar_items])
                .not_page(self)
                .select_related("teaser_image")
                .prefetch_related("teaser_image__renditions")
            )

        return sorted(
            latest_query_set, key=lambda x: x.newly_published_at, reverse=True
        )[:3]


class PageGalleryImage(Orderable):
    page = ParentalKey(Page, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey(
        get_image_model_string(), on_delete=models.SET_NULL, null=True, related_name="+"
    )
    alt_text = models.CharField(
        verbose_name=_("alternative text"),
        max_length=100,
        help_text=mark_safe(
            'Alternative (alt) text describes images when they fail to load, and is read aloud by assistive technologies. Use a maximum of 100 characters to describe your image. <a href="https://html.spec.whatwg.org/multipage/images.html#alt" target="_blank">Check the guidance for tips on writing alt text</a>.'
        ),
    )
    caption = RichTextField(
        features=["bold", "italic", "link"],
        help_text="An optional caption, which will be displayed directly below the image. This could be used for image sources or for other useful metadata.",
        blank=True,
    )

    class Meta(Orderable.Meta):
        verbose_name = _("gallery image")
        verbose_name_plural = _("gallery images")

    panels = [
        FieldPanel("image"),
        FieldPanel("alt_text"),
        FieldPanel("caption"),
    ]
