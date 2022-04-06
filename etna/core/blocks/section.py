from wagtail.core import blocks


class SectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        required=True, max_length=100, label="Section heading (heading level 2)"
    )

    class Meta:
        icon = "heading"
        label = "Section heading"
        template = "blocks/section_heading.html"
