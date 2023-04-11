from django.utils.translation import gettext_lazy as _

from wagtail import blocks


class TimePeriodBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, default="Explore by time period")

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


class LargeCardLinksBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, default="More to explore")
    page_1 = blocks.PageChooserBlock(label=_("Link one target"))
    page_2 = blocks.PageChooserBlock(label=_("Link two target"))

    class Meta:
        template = "blocks/large_links_block.html"
        icon = "th-large"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        page_1 = value["page_1"]
        page_2 = value["page_2"]
        link_pages = []
        if page_1 and page_1.live and page_1.specific.teaser_image:
            link_pages.append(page_1.specific)
        if page_2 and page_2.live and page_2.specific.teaser_image:
            link_pages.append(page_2.specific)
        context["link_pages"] = link_pages
        return context
