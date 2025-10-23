from wagtail import blocks

from app.core.blocks import (
    ContentTableBlock,
    DescriptionListBlock,
    DetailsBlock,
    DocumentsBlock,
    InsetTextBlock,
    ParagraphBlock,
    SubHeadingBlock,
)


class RequestContentBlock(blocks.StreamBlock):
    sub_heading = SubHeadingBlock()
    paragraph = ParagraphBlock()
    description_list = DescriptionListBlock()
    table = ContentTableBlock()
    details = DetailsBlock()
    document = DocumentsBlock()
    inset_text = InsetTextBlock()


class RequestSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = RequestContentBlock(required=False)

    class Meta:
        label = "Section"


class RequestStreamBlock(blocks.StreamBlock):
    content_section = RequestSectionBlock()
    paragraph = ParagraphBlock()
    description_list = DescriptionListBlock()
    table = ContentTableBlock()
    details = DetailsBlock()
    document = DocumentsBlock()
    inset_text = InsetTextBlock()


class ResponseContentBlock(blocks.StreamBlock):
    sub_heading = SubHeadingBlock()
    inset_text = InsetTextBlock()
    paragraph = ParagraphBlock()
    description_list = DescriptionListBlock()
    table = ContentTableBlock()
    details = DetailsBlock()
    document = DocumentsBlock()
    inset_text = InsetTextBlock()


class ResponseSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = ResponseContentBlock(required=False)

    class Meta:
        label = "Section"


class ResponseStreamBlock(blocks.StreamBlock):
    content_section = RequestSectionBlock()
    paragraph = ParagraphBlock()
    description_list = DescriptionListBlock()
    table = ContentTableBlock()
    details = DetailsBlock()
    document = DocumentsBlock()
    inset_text = InsetTextBlock()


class AnnexeContentBlock(blocks.StreamBlock):
    sub_heading = SubHeadingBlock()
    inset_text = InsetTextBlock()
    paragraph = ParagraphBlock()
    description_list = DescriptionListBlock()
    table = ContentTableBlock()
    details = DetailsBlock()
    document = DocumentsBlock()
    inset_text = InsetTextBlock()


class AnnexeSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = AnnexeContentBlock(required=False)

    class Meta:
        label = "Section"


class AnnexeStreamBlock(blocks.StreamBlock):
    content_section = RequestSectionBlock()
    paragraph = ParagraphBlock()
    description_list = DescriptionListBlock()
    table = ContentTableBlock()
    details = DetailsBlock()
    document = DocumentsBlock()
    inset_text = InsetTextBlock()
