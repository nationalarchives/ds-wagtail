from wagtail.core import blocks


class SectionHeadingBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        required=True,
        max_length=100,
        help_text="Section headings must be unique within the page.")

    class Meta:
        icon = 'fa-header'
        label = 'Section heading'
        template = 'sections/blocks/section-heading.html'
