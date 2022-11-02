from wagtail.core import blocks


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
    page = blocks.PageChooserBlock(page_type="collections.TopicExplorerIndexPage")

    class Meta:
        template = "collections/blocks/topic_explorer.html"
        help_text = "Outputs all topic child pages"
        icon = "th-large"
