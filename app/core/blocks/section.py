from django.utils.text import slugify
from wagtail import blocks

from .base import SectionDepthAwareStructBlock


class SectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        required=True, max_length=100, label="Section heading (heading level 2)"
    )

    class Meta:
        icon = "heading"
        label = "Section heading"

    def get_heading_id(self, value):
        return f"h2.{slugify(value['heading'])}"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context["heading_id"] = self.get_heading_id(value)
        return context


class SubHeadingBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, label="Sub-heading")

    class Meta:
        icon = "heading"
        label = "Sub-heading"


class SubSubHeadingBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, label="Sub-sub-heading")

    class Meta:
        icon = "heading"
        label = "Sub-sub-heading"
