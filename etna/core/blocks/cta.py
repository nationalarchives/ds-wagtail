from wagtail.core import blocks

# from etna.collections.blocks import (
#    TimePeriodExplorerIndexBlock,
#    TopicExplorerIndexBlock,
# )
#
from etna.core.blocks import (  # ContentImageBlock,
    PageListBlock,
    SectionDepthAwareStructBlock,
)



class TimePeriodBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, default="Explore by time period")
    sub_heading = blocks.CharBlock(
        max_length=200,
        default="Discover 1,000 years of British history through time periods including:",
    )
    page = blocks.PageChooserBlock(page_type="collections.TimePeriodExplorerIndexPage")

    class Meta:
        template = "collections/blocks/time_period_explorer.html"
        help_text = "Outputs all time period child pages"
        icon = "th-large"


class TopicExplorerBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, default="Explore by topic")
    sub_heading = blocks.CharBlock(
        max_length=200,
        default="Browse highlights of the collection through topics including:",
    )
    page = blocks.PageChooserBlock(page_type="collections.TopicExplorerIndexPage")

    class Meta:
        template = "collections/blocks/topic_explorer.html"
        help_text = "Outputs all topic child pages"
        icon = "th-large"




class TwoLargeImageLinks(blocks.StreamBlock):
    time_period = TimePeriodBlock()
    topic_explorer = TopicExplorerBlock()

    class Meta:
        block_counts = {
            "time_period": {"min_num": 1, "max_num": 1},
            "topic_explorer": {"min_num": 1, "max_num": 1},
        }


class FeaturedCollectionBlock(SectionDepthAwareStructBlock):

    items = PageListBlock(
        "insights.InsightsPage",
        exclude_drafts=True,
        exclude_private=False,
        select_related=["teaser_image"],
        min_num=3,
        max_num=9,
    )

    class Meta:
        icon = "list"
        label = "Featured collection"
        template = "insights/blocks/featured_collection.html"
