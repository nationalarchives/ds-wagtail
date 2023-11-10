from typing import Dict, List

from django.test import TestCase, override_settings

from wagtail.models import Page, Site

from etna.feedback.forms import FeedbackForm
from etna.feedback.models import FeedbackPrompt
from etna.feedback.tests import constants
from etna.feedback.widgets import ResponseSubmitButtonList


@override_settings(ALLOWED_HOSTS=[constants.VALID_DOMAIN])
class TestSubmissionFormValidation(TestCase):
    """
    Unit tests to cover all successful/unsucessful form validation scenarios.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.default_prompt = FeedbackPrompt.objects.get()
        cls.default_response_options = cls.default_prompt.response_options
        cls.valid_response_id = str(cls.default_response_options[0].id)

        # Pages don't have any revisions by default, so let's create one
        # for a page and mark it as the latest
        page = Page.objects.get(depth=2).specific
        page.teaser_text = "New teaser text"
        page.intro = "New intro text"
        revision = page.save_revision(clean=False, changed=True)
        page.latest_revision = revision
        page.save(update_fields=["latest_revision"])
        cls.page = page
        cls.page_revision = revision

    def get_form(self, data=None):
        return FeedbackForm(
            response_options=self.default_response_options,
            response_label=self.default_prompt.text,
            data=data,
        )

    def assertFieldErrorsEqual(
        self, form: FeedbackForm, field_name: str, expected_errors: List[Dict[str, str]]
    ):
        form_errors = form.errors.get_json_data()
        self.assertIn(field_name, form_errors)
        self.assertEqual(form_errors[field_name], expected_errors)

    def test_response_field_widget_set_on_init(self):
        form = self.get_form()
        widget = form.fields["response"].widget
        self.assertIsInstance(widget, ResponseSubmitButtonList)
        self.assertEqual(
            widget.choices,
            [
                (option.id, option.value["label"])
                for option in self.default_response_options
            ],
        )
        self.assertEqual(
            widget.icons,
            {
                option.id: option.value["icon"]
                for option in self.default_response_options
            },
        )
        self.assertEqual(
            widget.sentiments,
            {
                option.id: option.value["sentiment"]
                for option in self.default_response_options
            },
        )

    def test_invalid_response_format(self):
        form = self.get_form(
            data={
                "response": "not-a-uuid",
                "url": constants.VALID_URL,
            },
        )
        self.assertFieldErrorsEqual(
            form,
            "response",
            [
                {
                    "message": "Select a valid choice. not-a-uuid is not one of the available choices.",
                    "code": "invalid_choice",
                }
            ],
        )

    def test_invalid_response_choice(self):
        form = self.get_form(
            data={
                "response": "68526cc2-4461-475b-a02c-539181ed1cd3",
                "url": constants.VALID_URL,
            },
        )
        self.assertFieldErrorsEqual(
            form,
            "response",
            [
                {
                    "message": "Select a valid choice. 68526cc2-4461-475b-a02c-539181ed1cd3 is not one of the available choices.",
                    "code": "invalid_choice",
                }
            ],
        )

    def test_invalid_url_format(self):
        form = self.get_form(
            data={
                "response": self.valid_response_id,
                "url": constants.INVALID_URL,
            },
        )
        self.assertFieldErrorsEqual(
            form,
            "url",
            [
                {
                    "message": "Enter a valid URL.",
                    "code": "invalid",
                }
            ],
        )

    def test_url_invalid_when_no_matching_wagtail_site(self):
        Site.objects.all().delete()
        form = self.get_form(
            data={
                "response": self.valid_response_id,
                "url": constants.VALID_URL,
            },
        )
        self.assertFieldErrorsEqual(
            form,
            "url",
            [
                {
                    "message": "value could not be matched to a Wagtail site.",
                    "code": "invalid",
                }
            ],
        )

    def test_url_hostname_invalid_when_not_in_allowed_hosts(self):
        form = self.get_form(
            data={
                "response": self.valid_response_id,
                "url": constants.INVALID_DOMAIN_URL,
            },
        )
        self.assertFieldErrorsEqual(
            form,
            "url",
            [
                {
                    "message": "url hostname is invalid.",
                    "code": "invalid",
                }
            ],
        )

    @override_settings(ALLOWED_HOSTS=["*"])
    def test_url_hostname_valid_when_allowed_hosts_allows(self):
        form = self.get_form(
            data={
                "response": self.valid_response_id,
                "url": constants.INVALID_DOMAIN_URL,
            },
        )
        self.assertFalse(form.errors)

    def test_missing_page_revision(self):
        form = self.get_form(
            data={
                "response": self.valid_response_id,
                "url": constants.VALID_URL,
                "page": self.page,
            },
        )
        self.assertFieldErrorsEqual(
            form,
            "page_revision",
            [
                {
                    "message": "this field is required when 'page' is provided.",
                    "code": "required",
                }
            ],
        )

    def test_unexpected_page_revision(self):
        form = self.get_form(
            data={
                "response": self.valid_response_id,
                "url": constants.VALID_URL,
                "page_revision": self.page_revision.id,
            },
        )
        self.assertFieldErrorsEqual(
            form,
            "page_revision",
            [
                {
                    "message": "this field should only be provided when 'page' is also provided.",
                    "code": "unexpected",
                }
            ],
        )

    def test_page_and_page_revision_mismatch(self):
        # Used to test page/revision mismatch
        form = self.get_form(
            data={
                "response": self.valid_response_id,
                "url": constants.VALID_URL,
                "page": Page.objects.get(depth=1),
                "page_revision": self.page_revision.id,
            },
        )
        self.assertFieldErrorsEqual(
            form,
            "page_revision",
            [
                {
                    "message": "the specified revision does not match the specified 'page'.",
                    "code": "mismatch",
                }
            ],
        )
