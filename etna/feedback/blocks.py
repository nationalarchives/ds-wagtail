from django.utils.translation import gettext_lazy as _

from wagtail import blocks

from etna.feedback import constants


class ResponseOptionBlock(blocks.StructBlock):
    icon = blocks.ChoiceBlock(
        required=False,
        choices=(
            ("images/thumb-up.png", _("Thumbs up")),
            ("images/thumb-down.png", _("Thumbs down")),
        ),
    )
    label = blocks.CharBlock(
        label=_("label"), max_length=constants.RESPONSE_LABEL_MAX_LENGTH
    )
    sentiment = blocks.ChoiceBlock(
        label=_("sentiment"),
        choices=constants.SentimentChoices.choices,
        default=constants.SentimentChoices.NEUTRAL,
    )
