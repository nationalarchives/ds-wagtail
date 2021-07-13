from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock


class CollectionHighlightsBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, default="Collection Highlights")

    class Meta:
        template = "collections/blocks/collection_highlights.html"
        help_text = "Block used to output the list of collection highlights"
        icon = "fa-th"


class FeaturedPageBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100)
    page = blocks.PageChooserBlock()

    class Meta:
        template = "collections/blocks/featured_page.html"
        help_text = "Block used feature a page from within Wagtail"
        icon = "fa-arrow-up"


class PromotedItemBlock(blocks.StructBlock):
    url = blocks.URLBlock(label="external URL", help_text="URL for the external page")
    title = blocks.CharBlock(max_length=100, help_text="Title of the promoted page")
    teaser_image = ImageChooserBlock(
        help_text="An image used to create a teaser for the promoted page"
    )
    description = blocks.CharBlock(
        max_length=200, help_text="A description of the promoted page"
    )


class PromotedPagesBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100)
    sub_heading = blocks.CharBlock(max_length=200)
    promoted_items = blocks.ListBlock(PromotedItemBlock, min=3, max=3)

    class Meta:
        template = "collections/blocks/promoted_pages.html"
        help_text = "Block used promote external pages"
        icon = "fa-th-large"


class TopicExplorerIndexBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, default="Explore by topic")
    sub_heading = blocks.CharBlock(
        max_length=200,
        default="Browse highlights of the collection through topics including:",
    )
    page = blocks.PageChooserBlock(page_type="collections.TopicExplorerIndexPage")

    class Meta:
        template = "collections/blocks/topic_explorer.html"
        help_text = "Outputs all topic child pages"
        icon = "fa-th-large"


class TimePeriodExplorerIndexBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, default="Explore by time period")
    sub_heading = blocks.CharBlock(
        max_length=200,
        default="Discover 1,000 years of British history through time periods including:",
    )
    page = blocks.PageChooserBlock(page_type="collections.TimePeriodExplorerIndexPage")

    class Meta:
        template = "collections/blocks/time_period_explorer.html"
        help_text = "Outputs all time period child pages"
        icon = "fa-th-large"


class ExplorerIndexPageStreamBlock(blocks.StreamBlock):
    time_period_explorer_index = TimePeriodExplorerIndexBlock()
    topic_explorer_explorer_index = TopicExplorerIndexBlock()

    class Meta:
        block_counts = {
            "time_period_explorer": {"min_num": 1, "max_num": 1},
            "topic_explorer_explorer": {"min_num": 1, "max_num": 1},
        }


class TimePeriodExplorerPageStreamBlock(blocks.StreamBlock):
    collection_highlights = CollectionHighlightsBlock()
    featured_page = FeaturedPageBlock()
    promoted_pages = PromotedPagesBlock()

    class Meta:
        block_counts = {
            "collection_highlights": {"min_num": 1, "max_num": 1},
            "featured_page": {"max_num": 1},
            "promoted_pages": {"max_num": 1},
        }


class TopicExplorerPageStreamBlock(blocks.StreamBlock):
    collection_highlights = CollectionHighlightsBlock()
    featured_page = FeaturedPageBlock()
    promoted_pages = PromotedPagesBlock()

    class Meta:
        block_counts = {
            "collection_highlights": {"min_num": 1, "max_num": 1},
            "featured_page": {"max_num": 1},
            "promoted_pages": {"max_num": 1},
        }
