import uuid

from typing import Union

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Case, IntegerField, Q, When
from django.db.models.functions import Length
from django.utils.functional import cached_property
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin import panels
from wagtail.fields import RichTextField, StreamField
from wagtail.models import DraftStateMixin, Orderable, Page, RevisionMixin
from wagtail.snippets.models import register_snippet

from etna.feedback import constants
from etna.feedback.blocks import ResponseOptionBlock
from etna.feedback.utils import normalize_path
from etna.feedback.widgets import PageTypeChooser


class FeedbackPromptManager(models.Manager):
    def get_for_path(
        self, path: str, page: Page | None
    ) -> Union["FeedbackPrompt", None]:
        """
        Return the most appropriate `FeedbackPrompt` instance for the
        supplied `path`.
        """
        path = normalize_path(path)
        presceeding_paths = [path[:i] for i in range(1, len(path))]

        if path.endswith("/"):
            # Allow prompts that have been defined without a trailing
            # slash to be matched to this request
            exact_path_variations = (path, path.rstrip("/"))
        else:
            # If the prompt has been defined with a trailing slash, but
            # this request does not have one, do not allow a match
            exact_path_variations = (path,)

        for match in (
            self.filter(live=True)
            .prefetch_related("for_page_types")
            .annotate(
                match=Case(
                    When(
                        path__in=exact_path_variations,
                        startswith_path=False,
                        then=constants.MATCH_EXACT_PATH,
                    ),
                    When(
                        path=exact_path_variations,
                        startswith_path=True,
                        then=constants.MATCH_EXACT_PATH_WITH_SUB_PATHS,
                    ),
                    default=constants.MATCH_SUB_PATH,
                    output_field=IntegerField(),
                )
            )
            .filter(
                Q(path__in=exact_path_variations)
                | Q(path__in=presceeding_paths, startswith_path=True)
            )
            .order_by("match", Length("path").desc(), "id")
        ):
            if isinstance(page, Page):
                page_ctype = ContentType.objects.get_for_id(page.content_type_id)
            else:
                page_ctype = None
            valid_ctypes = set(obj.content_type for obj in match.for_page_types.all())

            if valid_ctypes and (page_ctype is None or page_ctype not in valid_ctypes):
                continue

            # checks passed! return this match
            return match

        raise FeedbackPrompt.DoesNotExist

    def get_by_natural_key(self, public_id: Union[str, uuid.UUID]) -> "FeedbackPrompt":
        return self.get(public_id=public_id)


class FeedbackPromptPageType(Orderable):
    prompt = ParentalKey("feedback.FeedbackPrompt", related_name="for_page_types")
    ctype = models.ForeignKey(
        ContentType, verbose_name="type", on_delete=models.PROTECT
    )

    panels = [panels.FieldPanel("ctype", widget=PageTypeChooser)]

    @property
    def content_type(self):
        return ContentType.objects.get_for_id(self.ctype_id)


@register_snippet
class FeedbackPrompt(DraftStateMixin, RevisionMixin, ClusterableModel):
    public_id = models.UUIDField(
        editable=False, unique=True, default=uuid.uuid4, verbose_name=_("public ID")
    )
    text = models.CharField(
        verbose_name=_("prompt text"),
        max_length=constants.PROMPT_TEXT_MAX_LENGTH,
        default="What did you think of this page?",
    )
    response_options = StreamField(
        [("option", ResponseOptionBlock())],
        verbose_name=_("response options"),
    )
    thank_you_heading = models.CharField(
        max_length=100,
        verbose_name=_("thank you heading"),
        default=_("Thank you for your valuable feedback"),
        help_text=_("Displayed to users after succesfully submitting feedback."),
    )
    thank_you_message = RichTextField(
        max_length=200,
        verbose_name=_("thank you message"),
        features=settings.RESTRICTED_RICH_TEXT_FEATURES,
        help_text=_(
            "If supplied, displayed below the 'Thank you heading' when a user succesfully submits feedback."
        ),
        blank=True,
    )
    continue_link_text = models.CharField(
        max_length=200,
        default=_("Return to the previous page"),
        help_text=_(
            'After submitting feedback, non-JS users are taken to a success page, where the thank you headding and text are displayed, followed by a link to return to the previous page. This field can be used to change the text of that link. For example, "Continue with your search" might make more sense to users.'
        ),
    )
    path = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_("use for path"),
        help_text=_(
            'The URL path this prompt should be displayed on. For example: "/search/catalogue/".'
        ),
    )
    startswith_path = models.BooleanField(
        verbose_name=_("also match paths that start with the above"),
        default=False,
    )
    revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="feedbackprompt"
    )

    objects = FeedbackPromptManager()

    panels = [
        panels.MultiFieldPanel(
            heading=_("Prompt form"),
            children=[
                panels.FieldPanel("text"),
                panels.FieldPanel("response_options"),
            ],
        ),
        panels.MultiFieldPanel(
            heading=_("Success page"),
            children=[
                panels.FieldPanel("thank_you_heading"),
                panels.FieldPanel("thank_you_message"),
                panels.FieldPanel("continue_link_text"),
            ],
        ),
        panels.MultiFieldPanel(
            heading=_("Visibility options"),
            children=[
                panels.FieldPanel("path"),
                panels.FieldPanel("startswith_path"),
            ],
        ),
        panels.InlinePanel(
            "for_page_types", heading=_("Page type must be one of"), label="Page type"
        ),
    ]

    class Meta:
        ordering = ("path", "startswith_path")

    def natural_key(self):
        return (self.public_id,)

    def __str__(self):
        base = self.text
        if self.path == "/" and self.startswith_path:
            return base + " (default)"
        return base + f" ({self.display_path})"

    @cached_property
    def display_path(self) -> str:
        if self.startswith_path:
            return self.path + "*"
        return self.path

    def with_content_json(self, content):
        """
        Similar to :meth:`RevisionMixin.with_content_json`,
        but with the following fields also preserved:
        * ``public_id``
        * ``path``
        * ``startswith_path``
        """
        obj = super().with_content_json(content)

        # Ensure other values that are meaningful for the object as a whole (rather than
        # to a specific revision) are preserved
        obj.public_id = self.public_id
        obj.path = self.path
        obj.startswith_path = self.startswith_path

        return obj

    def clean(self, *args, **kwargs):
        self.path = normalize_path(self.path)
        return super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.path = normalize_path(self.path)
        return super().save(*args, **kwargs)


class FeedbackSubmission(models.Model):
    received_at = models.DateTimeField(auto_now_add=True, verbose_name=_("received at"))
    public_id = models.UUIDField(
        editable=False, unique=True, default=uuid.uuid4, verbose_name=_("public ID")
    )

    # Where the feedback was given
    full_url = models.TextField(verbose_name=_("full URL"), editable=False)
    site = models.ForeignKey(
        "wagtailcore.Site",
        verbose_name=_("site"),
        on_delete=models.PROTECT,
        editable=False,
    )
    page_type = models.TextField(verbose_name=_("page type"), null=True, editable=False)
    page_title = models.TextField(
        verbose_name=_("page title"), null=True, editable=False
    )
    path = models.CharField(
        max_length=255, db_index=True, verbose_name=_("path"), editable=False
    )
    query_params = models.JSONField(
        default=dict, verbose_name=_("query params"), editable=False
    )

    # Common feedback values
    prompt_text = models.CharField(
        max_length=constants.PROMPT_TEXT_MAX_LENGTH,
        verbose_name=_("prompt text"),
        editable=False,
    )
    response_sentiment = models.SmallIntegerField(
        db_index=True, verbose_name=_("response sentiment"), editable=False
    )
    response_label = models.CharField(
        max_length=constants.RESPONSE_LABEL_MAX_LENGTH,
        db_index=True,
        verbose_name=_("response label"),
        editable=False,
    )
    comment_prompt_text = models.CharField(
        max_length=constants.COMMENT_PROMPT_TEXT_MAX_LENGTH,
        verbose_name=_("comment prompt text"),
        editable=False,
    )
    comment = models.TextField(verbose_name=_("comment"), editable=False)

    # Additional metadata
    prompt = models.ForeignKey(
        FeedbackPrompt,
        verbose_name=_("prompt"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="submissions",
        editable=False,
    )
    prompt_revision = models.ForeignKey(
        "wagtailcore.Revision",
        null=True,
        verbose_name=_("prompt revision"),
        on_delete=models.SET_NULL,
        related_name="+",
        editable=False,
    )
    page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("wagtail page"),
        editable=False,
    )
    page_revision = models.ForeignKey(
        "wagtailcore.Revision",
        null=True,
        verbose_name=_("page revision"),
        on_delete=models.SET_NULL,
        related_name="+",
        editable=False,
    )
    page_revision_published = models.DateTimeField(
        null=True,
        verbose_name=_("page revision published at"),
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("user"),
        editable=False,
    )

    class Meta:
        ordering = ("-received_at", "-id")

    def sentiment_label(self) -> str:
        try:
            return constants.SENTIMENT_LABELS[self.response_sentiment]
        except KeyError:
            return str(self.response_sentiment)

    sentiment_label.short_description = _("Sentiment label")

    def comment_truncated(self):
        return Truncator(self.comment).chars(100)

    comment_truncated.admin_order_field = "comment"
    comment_truncated.short_description = _("Comment")

    def response(self):
        return f"{self.response_label} ({self.sentiment_label()})"

    response.admin_order_field = "response_label"
    response.short_description = _("Response")
