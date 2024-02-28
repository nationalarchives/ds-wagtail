from django.utils.translation import gettext_lazy as _

from wagtail import blocks

from etna.feedback import constants


class ResponseOptionBlock(blocks.StructBlock):
    icon = blocks.ChoiceBlock(
        label=_("Icon"),
        required=False,
        choices=(
            ("images/thumb-up.png", _("Thumbs up")),
            ("images/thumb-down.png", _("Thumbs down")),
        ),
    )
    label = blocks.CharBlock(
        label=_("Label"), max_length=constants.RESPONSE_LABEL_MAX_LENGTH
    )
    sentiment = blocks.ChoiceBlock(
        label=_("Sentiment"),
        choices=constants.SentimentChoices.choices,
        default=constants.SentimentChoices.NEUTRAL,
    )
    comment_prompt_text = blocks.CharBlock(
        label=_("Comment prompt text"),
        blank=True,
        default=constants.DEFAULT_COMMENT_PROMPT_TEXT,
        max_length=constants.COMMENT_PROMPT_TEXT_MAX_LENGTH,
        help_text=_(
            "The text that is displayed to users after responding with this feedback option, "
            "prompting them to leave an optional comment to support their feedback. Leave this "
            "field blank to avoid prompting users for a comment when this response option is used."
        ),
    )
