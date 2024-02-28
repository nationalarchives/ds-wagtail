from django.db.models import IntegerChoices
from django.utils.translation import gettext_lazy as _

PROMPT_TEXT_MAX_LENGTH = 200
COMMENT_PROMPT_TEXT_MAX_LENGTH = 200
RESPONSE_LABEL_MAX_LENGTH = 100
COMMENT_MAX_LENGTH = 500
DEFAULT_COMMENT_PROMPT_TEXT = _("Can you tell us more about why you answered this way?")

# Used by FeedbackPromptManager.get_for_path()
MATCH_EXACT_PATH = 1
MATCH_EXACT_PATH_WITH_SUB_PATHS = 2
MATCH_SUB_PATH = 3


# Used by ResponseOptionBlock
class SentimentChoices(IntegerChoices):
    V_NEGATIVE = -2, _("Very negative")
    NEGATIVE = -1, _("Negative")
    NEUTRAL = 0, _("Neutral")
    POSITIVE = 1, _("Positive")
    V_POSITIVE = 2, _("Very positive")


SENTIMENT_LABELS = dict(SentimentChoices.choices)
