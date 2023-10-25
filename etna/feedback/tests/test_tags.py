from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from django.test import TestCase, override_settings
from django.urls import resolve, reverse

from wagtail.models import Page

from etna.feedback.models import FeedbackPrompt
from etna.feedback.templatetags.feedback_tags import render_feedback_prompt
from etna.home.models import HomePage


def fake_request_context(path: str, page: Page | None = None):
    request = HttpRequest()
    request.META["SERVER_NAME"] = "localhost"
    request.META["SERVER_PORT"] = "8000"
    request.path = path
    request.resolver_match = resolve(path)
    return {"request": request, "page": page}


class TestRenderFeedbackPromptTag(TestCase):
    """
    Unit tests for `{% render_feedback_prompt %}`
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.default_prompt = FeedbackPrompt.objects.get()
        cls.default_prompt.save_revision().publish()
        cls.home_path = "/"
        cls.home_url = "http://localhost:8000/"
        cls.page = HomePage(
            title="Page",
            id=1,
            slug="page",
            live_revision_id=1,
            content_type=ContentType.objects.get_for_model(HomePage),
        )
        cls.url_kwargs = {
            "prompt_id": cls.default_prompt.public_id,
            "version": cls.default_prompt.live_revision_id,
        }

    @override_settings(FEATURE_FEEDBACK_MECHANISM_ENABLED=True)
    def test_prompt_rendering_for_path(self):
        with self.assertNumQueries(2):
            result = render_feedback_prompt(fake_request_context(self.home_path))
        self.assertTrue(result)
        self.assertInHTML(f"<legend>{self.default_prompt.text}</legend>", result)
        self.assertInHTML(
            f'<input type="hidden" name="url" value="{self.home_url}" id="id_url">',
            result,
        )
        self.assertInHTML('<input type="hidden" name="page" id="id_page">', result)
        self.assertInHTML(
            '<input type="hidden" name="page_revision" id="id_page_revision">', result
        )
        self.assertInHTML(
            f'<h3 class="tna-heading-m feedback__success-heading">{self.default_prompt.thank_you_heading}</h3>',
            result,
        )

    @override_settings(FEATURE_FEEDBACK_MECHANISM_ENABLED=True)
    def test_prompt_rendering_for_page(self):
        with self.assertNumQueries(2):
            result = render_feedback_prompt(
                fake_request_context(self.home_path, page=self.page)
            )
        self.assertTrue(result)
        self.assertInHTML(f"<legend>{self.default_prompt.text}</legend>", result)
        self.assertInHTML(
            f'<input type="hidden" name="url" value="{self.home_url}" id="id_url">',
            result,
        )
        self.assertInHTML(
            f'<input type="hidden" name="page" id="id_page" value="{self.page.id}">',
            result,
        )
        self.assertInHTML(
            f'<input type="hidden" name="page_revision" id="id_page_revision" value="{self.page.live_revision_id}">',
            result,
        )
        self.assertInHTML(
            f'<input type="hidden" name="page_type" id="id_page_type" value="{self.page.page_type_display_name}">',
            result,
        )
        self.assertInHTML(
            f'<input type="hidden" name="page_title" id="id_page_title" value="{self.page.title}">',
            result,
        )
        self.assertInHTML(
            f'<h3 class="tna-heading-m feedback__success-heading">{self.default_prompt.thank_you_heading}</h3>',
            result,
        )

    @override_settings(FEATURE_FEEDBACK_MECHANISM_ENABLED=True)
    def test_prompt_not_rendered_for_feedback_urls(self):
        for path in (
            reverse("feedback:success", kwargs=self.url_kwargs),
            reverse("feedback:comment_success", kwargs=self.url_kwargs),
        ):
            with self.subTest(path):
                with self.assertNumQueries(0):
                    result = render_feedback_prompt(
                        fake_request_context(path, page=self.page)
                    )
                    self.assertFalse(result)

    @override_settings(FEATURE_FEEDBACK_MECHANISM_ENABLED=False)
    def test_prompt_not_rendered_when_disabled(self):
        with self.assertNumQueries(0):
            result = render_feedback_prompt(
                fake_request_context(self.home_path, page=self.page)
            )
            self.assertFalse(result)
