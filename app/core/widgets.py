from wagtail.admin.rich_text.editors.draftail import DraftailRichTextArea


class CustomDraftailRichTextArea(DraftailRichTextArea):
    """
    Custom Draftail Rich Text Area to remove placeholder text from RichTextFields/widgets.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the placeholder with None to remove placeholder text from RichTextFields
        self.options["placeholder"] = None
