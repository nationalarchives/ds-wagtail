from wagtail import blocks

from .page_chooser import APIPageChooserBlock


class FeaturedRecordArticleBlock(blocks.StructBlock):
    page = APIPageChooserBlock(
        label="Page",
        page_type="wagtailcore.Page",
        api_fields=["teaser_image", "type_label", "is_newly_published"],
        rendition_size="fill-500x500",
        jpeg_quality=60,
        webp_quality=80,
    )

    class Meta:
        icon = "doc-empty-inverse"
        template = "blocks/featured_record_article.html"
        label = "Featured record article"
