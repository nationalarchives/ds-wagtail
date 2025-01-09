from django.conf import settings
from django.core.exceptions import ValidationError
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


class ButtonBlock(blocks.StructBlock):
    label = blocks.CharBlock()
    link = APIPageChooserBlock(required=False)
    external_link = blocks.URLBlock(required=False)
    accented = blocks.BooleanBlock(
        required=False,
        help_text="Use the accented button style",
        label="Accented",
    )

    def clean(self, value):
        data = super().clean(value)

        if data.get("link") and data.get("external_link"):
            raise ValidationError(
                "You must provide either a page link or an external link, not both."
            )
        elif not (data.get("link") or data.get("external_link")):
            raise ValidationError(
                "You must provide either a page link or an external link."
            )

        return data

    def get_api_representation(self, value, context=None):
        representation = {
            "label": value["label"],
            "href": value.get("external_link") or value["link"].full_url,
            "accent": value.get("accented") or False,
        }

        return representation

    class Meta:
        icon = "link"
        label = "Button"


class CallToActionBlock(blocks.StructBlock):
    body = APIRichTextBlock(
        max_length=100, features=settings.RESTRICTED_RICH_TEXT_FEATURES
    )
    button = ButtonBlock()

    class Meta:
        icon = "link"
        label = "Call to action"
