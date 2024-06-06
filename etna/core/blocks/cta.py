from django.conf import settings
from django.utils.translation import gettext_lazy as _

from wagtail import blocks

from .page_chooser import APIPageChooserBlock
from .paragraph import APIRichTextBlock


class LargeCardLinksBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, required=False)
    page_1 = APIPageChooserBlock(
        label=_("Link one target"), required_api_fields=["teaser_image"]
    )
    page_2 = APIPageChooserBlock(
        label=_("Link two target"), required_api_fields=["teaser_image"]
    )

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

class CallToActionBlock(blocks.StructBlock):
    body = APIRichTextBlock(max_length=100, features=settings.RESTRICTED_RICH_TEXT_FEATURES)
    label = blocks.CharBlock()
    link = APIPageChooserBlock()

    class Meta:
        icon = "arrow-right"
        template = "blocks/call_to_action_block.html"