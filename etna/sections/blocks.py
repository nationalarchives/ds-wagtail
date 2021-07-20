from wagtail.core import blocks


class SectionHeadingBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=True, max_length=100)
    section_id = blocks.CharBlock(required=False, max_length=50)

    class Meta:
        icon = 'fa-header'
        label = 'Section heading'
        template = 'sections/blocks/section-heading.html'
