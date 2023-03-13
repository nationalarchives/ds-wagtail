from django.utils.text import slugify

from wagtail import blocks


class SectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        required=True, max_length=100, label="Section heading (heading level 2)"
    )

    class Meta:
        icon = "heading"
        label = "Section heading"
        template = "blocks/section_heading.html"

    def get_heading_id(self, value):
        return f"h2.{slugify(value['heading'])}"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context["heading_id"] = self.get_heading_id(value)
        return context
