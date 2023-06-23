import uuid

from http import HTTPStatus

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.http import urlencode

from wagtail.models import Page, Site
from wagtail.test.utils import WagtailTestUtils

from etna.core.test_utils import prevent_request_warnings
from etna.feedback.constants import SentimentChoices
from etna.feedback.models import FeedbackPrompt, FeedbackSubmission
from etna.feedback.utils import sign_submission_id

from .constants import VALID_URL


@override_settings(ALLOWED_HOSTS=["*"])
class TestFeedbackSubmitView(WagtailTestUtils, TestCase):
    """
    Integration tests for `etna.feedback.views.FeedbackSubmitView`,
    utilising Django's full request/response cycle, including URL resolution.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.prompt = FeedbackPrompt.objects.get()
        cls.positive_response_option = cls.prompt.response_options[0]
        cls.negative_response_option = cls.prompt.response_options[1]

        cls.url = reverse(
            "feedback:submit",
            kwargs={
                "prompt_id": cls.prompt.public_id,
                "version": cls.prompt.live_revision_id,
            },
        )
        cls.success_url = reverse(
            "feedback:success",
            kwargs={
                "prompt_id": cls.prompt.public_id,
                "version": cls.prompt.live_revision_id,
            },
        )

        # Pages don't have any revisions by default, so let's create one
        # and mark it as the latest
        page = Page.objects.get(depth=2).specific
        page.teaser_text = "New teaser text"
        revision = page.save_revision(clean=False, changed=True)
        revision.publish()
        cls.page = page
        cls.page_revision = revision

    @prevent_request_warnings
    def test_get_requests_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    @prevent_request_warnings
    def test_raises_404_if_version_not_recognised(self):
        url = self.url.replace(str(self.prompt.live_revision_id), "999")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @prevent_request_warnings
    def test_raises_404_if_prompt_id_is_invalid(self):
        url = self.url.replace(
            str(self.prompt.public_id), "7cca5b94-3da0-4057-af60-0b0dc45451cb"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @prevent_request_warnings
    def test_raises_404_if_version_does_not_match_the_prompt(self):
        url = self.url.replace(
            str(self.prompt.live_revision_id), str(self.page_revision.id)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_valid_regular(self):
        test_user = self.create_user("test")
        self.client.force_login(test_user)

        for response_option in (
            self.positive_response_option,
            self.negative_response_option,
        ):
            with self.subTest(response_option.value["label"]):
                response = self.client.post(
                    self.url,
                    data={
                        "url": [VALID_URL],
                        "response": [response_option.id],
                    },
                )

                submission = FeedbackSubmission.objects.order_by("id").last()
                querystring = urlencode(
                    {"next": VALID_URL, "submission": submission.public_id}
                )
                self.assertRedirects(response, self.success_url + "?" + querystring)

                self.assertEqual(submission.full_url, VALID_URL)
                self.assertEqual(submission.path, "/some-url")
                self.assertEqual(submission.prompt, self.prompt)
                self.assertEqual(
                    submission.response_sentiment, response_option.value["sentiment"]
                )
                self.assertEqual(
                    submission.response_label, response_option.value["label"]
                )
                self.assertEqual(
                    submission.comment_prompt_text,
                    response_option.value["comment_prompt_text"],
                )
                self.assertEqual(submission.user, test_user)
                self.assertIsNone(submission.page)
                self.assertIsNone(submission.page_revision)

    def test_post_valid_ajax(self):
        test_user = self.create_user("test")
        self.client.force_login(test_user)

        for response_option in (
            self.positive_response_option,
            self.negative_response_option,
        ):
            with self.subTest(response_option.value["label"]):
                response = self.client.post(
                    self.url,
                    data={
                        "is_ajax": "true",
                        "url": VALID_URL,
                        "response": response_option.id,
                    },
                )

                submission = FeedbackSubmission.objects.order_by("id").last()
                self.assertEqual(
                    response.json(),
                    {
                        "id": str(submission.public_id),
                        "signature": sign_submission_id(submission.public_id),
                        "comment_prompt_text": response_option.value[
                            "comment_prompt_text"
                        ],
                    },
                )

                self.assertEqual(submission.full_url, VALID_URL)
                self.assertEqual(submission.path, "/some-url")
                self.assertEqual(submission.prompt, self.prompt)
                self.assertEqual(
                    submission.response_sentiment, response_option.value["sentiment"]
                )
                self.assertEqual(
                    submission.response_label, response_option.value["label"]
                )
                self.assertEqual(
                    submission.comment_prompt_text,
                    response_option.value["comment_prompt_text"],
                )
                self.assertEqual(submission.user, test_user)
                self.assertIsNone(submission.page)
                self.assertIsNone(submission.page_revision)

    @prevent_request_warnings
    def test_post_invalid_regular(self):
        post_data = {
            "response": ["invalid-response-id"],
            "url": [VALID_URL],
        }
        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "success": False,
                "form_data": post_data,
                "errors": {
                    "response": [
                        "Select a valid choice. invalid-response-id is not one of the available choices."
                    ],
                },
            },
        )


@override_settings(ALLOWED_HOSTS=["*"])
class TestFeedbackCommentSubmitView(WagtailTestUtils, TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.url = reverse("feedback:submit_comment")
        cls.prompt = FeedbackPrompt.objects.get()

        # Create a submission to comment on
        cls.submission = FeedbackSubmission.objects.create(
            site=Site.objects.first(),
            full_url="",
            path="",
            prompt_text="prompt",
            response_sentiment=SentimentChoices.POSITIVE,
            response_label="Easy to use",
            comment_prompt_text="Thank you! Can you tell us more about why you answered this way?",
        )

    @prevent_request_warnings
    def test_get_requests_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_post_with_valid_data(self):
        response = self.client.post(
            self.url,
            data={
                "comment": "This is a comment",
                "submission": self.submission.public_id,
                "signature": sign_submission_id(self.submission.public_id),
            },
        )

        # Test view response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})

        # Test the comment was saved
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.comment, "This is a comment")

    @prevent_request_warnings
    def test_post_with_missing_submission_and_signature(self):
        post_data = {
            "comment": ["This is a comment"],
        }
        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "success": False,
                "form_data": post_data,
                "errors": {
                    "signature": ["This field is required."],
                    "submission": ["This field is required."],
                },
            },
        )

    @prevent_request_warnings
    def test_post_with_invalid_submission_id(self):
        post_data = {
            "comment": ["This is a comment"],
            "submission": ["invalid-submission-id"],
            "signature": ["test"],
        }
        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "success": False,
                "form_data": post_data,
                "errors": {
                    "submission": ["“invalid-submission-id” is not a valid UUID."],
                },
            },
        )

    @prevent_request_warnings
    def test_post_with_invalid_signature(self):
        post_data = {
            "comment": ["This is a comment"],
            "submission": [str(self.submission.public_id)],
            "signature": ["invalid-signature"],
        }
        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "success": False,
                "form_data": post_data,
                "errors": {
                    "signature": ["Value does not match the specified submission."],
                },
            },
        )


class TestFeedbackSuccessView(TestCase):
    """
    Integration tests for `etna.feedback.views.FeedbackSuccessView`,
    utilising Django's full request/response cycle, including URL resolution.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.prompt = FeedbackPrompt.objects.get()
        cls.url = reverse(
            "feedback:success",
            kwargs={
                "prompt_id": cls.prompt.public_id,
                "version": cls.prompt.live_revision_id,
            },
        )
        cls.next_url = "/some-path"
        cls.valid_submission_id = uuid.uuid4()

    def test_golden_path(self):
        response = self.client.get(
            self.url, {"submission": self.valid_submission_id, "next": self.next_url}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["prompt"], self.prompt)
        self.assertEqual(response.context["next_url"], self.next_url)
        self.assertEqual(
            response.context["submission_id"], str(self.valid_submission_id)
        )
        self.assertContains(response, self.prompt.thank_you_heading)
        self.assertContains(
            response,
            f'<a href="{self.next_url}" class="tna-button--dark">{self.prompt.continue_link_text}</a>',
        )

    def test_invalid_submission_id(self):
        invalid_submission_id = "not-a-uuid"

        response = self.client.get(
            self.url, {"submission": invalid_submission_id, "next": self.next_url}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["prompt"], self.prompt)
        self.assertEqual(response.context["next_url"], self.next_url)
        self.assertIsNone(response.context["submission_id"])
        self.assertContains(response, self.prompt.thank_you_heading)
        self.assertContains(
            response,
            f'<a href="{self.next_url}" class="tna-button--dark">{self.prompt.continue_link_text}</a>',
        )

    def test_missing_next_url_substituded_with_homepage_path(self):
        response = self.client.get(self.url, {"submission": self.valid_submission_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["prompt"], self.prompt)
        self.assertEqual(response.context["next_url"], "/")
        self.assertEqual(
            response.context["submission_id"], str(self.valid_submission_id)
        )
        self.assertContains(response, self.prompt.thank_you_heading)
        self.assertContains(
            response,
            f'<a href="/" class="tna-button--dark">{self.prompt.continue_link_text}</a>',
        )


class TestSubmissionReportView(WagtailTestUtils, TestCase):
    """
    Integration tests for `etna.feedback.views.FeedbackSubmissionReportView`,
    utilising Django's full request/response cycle, including URL resolution.
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.url = reverse("feedback_submission_report")
        cls.login_url = reverse("wagtailadmin_login")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.super_user = cls.create_superuser("super")
        cls.normal_user = cls.create_user("normal")

    def test_access_permitted(self):
        self.client.force_login(self.super_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        export_response = self.client.get(self.url, data={"export": "csv"})
        self.assertEqual(export_response.status_code, 200)
        self.assertEqual(export_response.headers["Content-Type"], "text/csv")

    @prevent_request_warnings
    def test_access_not_permitted(self):
        expected_redirect_url = self.login_url + "?" + urlencode({"next": self.url})
        self.client.force_login(self.normal_user)
        response = self.client.get(self.url)
        self.assertRedirects(response, expected_redirect_url)
        export_response = self.client.get(self.url, export="csv")
        self.assertRedirects(export_response, expected_redirect_url)
