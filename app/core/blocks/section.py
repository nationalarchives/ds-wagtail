from wagtail import blocks


class SubHeadingBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Sub-heading")

    class Meta:
        icon = "heading"
        label = "Sub-heading"


class SubSubHeadingBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Sub-sub-heading")

    class Meta:
        icon = "heading"
        label = "Sub-sub-heading"
