from wagtail import blocks


class AccordionBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    content = blocks.RichTextBlock(required=True)

    class Meta:
        icon = "list-ul"
        label = "Accordion"


class AccordionsBlock(blocks.StructBlock):
    accordion = blocks.ListBlock(AccordionBlock())
