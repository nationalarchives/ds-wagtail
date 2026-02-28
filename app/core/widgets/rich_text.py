from wagtail.admin.rich_text.editors.draftail import DraftailRichTextArea


class CustomDraftailRichTextArea(DraftailRichTextArea):
    """
    Project-specific subclass of Wagtail's DraftailRichTextArea.

    Extend or override methods here for custom behaviour.
    Kept minimal to avoid breaking imports.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the placeholder with None to remove placeholder text from RichTextFields
        self.options["placeholder"] = None
