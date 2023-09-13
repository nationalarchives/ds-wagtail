from django import template
from django.conf import settings
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from wagtail.models import Page

from etna.feedback.forms import FeedbackCommentForm, FeedbackForm
from etna.feedback.models import FeedbackPrompt

register = template.Library()


@register.simple_tag(takes_context=True)
def render_feedback_prompt(context, template_name="feedback/includes/prompt.html"):
    request = context["request"]

    # Avoid rendering if not enabled
    if not settings.FEATURE_FEEDBACK_MECHANISM_ENABLED:
        return ""

    # Avoid rendering on feedback views
    if getattr(request.resolver_match, "namespace", "") == "feedback":
        return ""

    # Only continue if a valid prompt is available
    page = context.get("page")
    if not isinstance(page, Page):
        page = None
        page_type = context.get("page_type")
        page_title = context.get("page_title")
    else:
        page_type = page.page_type_display_name
        page_title = page.title

    try:
        prompt = FeedbackPrompt.objects.get_for_path(request.path, page=page)
    except FeedbackPrompt.DoesNotExist:
        return ""

    initial_data = {
        "url": request.build_absolute_uri(),
        "page_type": page_type,
        "page_title": page_title,
    }
    if page:
        initial_data["page"] = page.id
        initial_data["page_revision"] = page.live_revision_id

    form = FeedbackForm(
        response_options=prompt.response_options,
        response_label=prompt.text,
        initial=initial_data,
    )

    template = get_template(template_name)
    return mark_safe(
        template.render(
            {
                "request": request,
                "prompt": prompt,
                "form": form,
                "comment_form": FeedbackCommentForm(),
            }
        )
    )
