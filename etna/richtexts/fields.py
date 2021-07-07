from wagtail.core import fields

BASIC_RICH_TEXT_FEATURES = [
    "bold",
    "italic",
    "link",
]


class BasicRichTextField(fields.RichTextField):
    """A RichTextField with limited features
    http://docs.wagtail.io/en/v2.0/advanced_topics/customisation/page_editing_interface.html#limiting-features-in-a-rich-text-field
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.features = BASIC_RICH_TEXT_FEATURES
