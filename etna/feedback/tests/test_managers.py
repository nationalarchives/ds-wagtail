from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from wagtail.models import Page

from etna.feedback.models import FeedbackPrompt, FeedbackPromptPageType
from etna.generic_pages.models import GeneralPage
from etna.home.models import HomePage


class TestGetForPath(TestCase):
    """
    Unit tests for `FeedbackPromptManager.get_for_path()`
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.default_prompt = FeedbackPrompt.objects.get()

        # Create alternatives
        options = cls.default_prompt.response_options
        cls.search_section_prompt = FeedbackPrompt.objects.create(
            response_options=options,
            path="/search",
            startswith_path=True,
        )
        cls.search_view_prompt = FeedbackPrompt.objects.create(
            response_options=options,
            path="/search",
            startswith_path=False,
        )
        cls.search_result_prompt = FeedbackPrompt.objects.create(
            response_options=options,
            path="/search/result/",
            startswith_path=True,
        )

    def assertMatchForPath(
        self, path: str, expected_prompt: FeedbackPrompt, page: Page | None = None
    ):
        result = FeedbackPrompt.objects.get_for_path(path, page=page)
        self.assertEqual(result, expected_prompt)

    def test_matching(self):
        self.assertMatchForPath("/", self.default_prompt)
        self.assertMatchForPath("/path/to/some/sub/page", self.default_prompt)
        self.assertMatchForPath("/search/", self.search_view_prompt)
        self.assertMatchForPath("/SEARCH/", self.search_view_prompt)
        self.assertMatchForPath("/search", self.search_view_prompt)
        self.assertMatchForPath("/search/result/", self.search_result_prompt)
        self.assertMatchForPath("/search/result/ITEM_ID", self.search_result_prompt)
        self.assertMatchForPath("/search/result", self.search_section_prompt)
        self.assertMatchForPath("/search/sub-path", self.search_section_prompt)
        self.assertMatchForPath("/search/result-machine", self.search_section_prompt)

    def test_matching_for_page_type(self):
        path = "/not-root"
        genericpage_prompt = FeedbackPrompt.objects.create(
            response_options=self.default_prompt.response_options,
            path=path,
            startswith_path=True,
            for_page_types=[
                FeedbackPromptPageType(
                    ctype=ContentType.objects.get_for_model(GeneralPage)
                )
            ],
        )
        homepage_prompt = FeedbackPrompt.objects.create(
            response_options=self.default_prompt.response_options,
            path=path,
            startswith_path=True,
            for_page_types=[
                FeedbackPromptPageType(
                    ctype=ContentType.objects.get_for_model(HomePage)
                )
            ],
        )
        # Either page could match this one, but the more specific prompts above will
        # be checked first (because equal-chance prompts are ordered 'id' as a tie-break)
        FeedbackPrompt.objects.create(
            response_options=self.default_prompt.response_options,
            path=path,
            startswith_path=True,
            for_page_types=[
                FeedbackPromptPageType(
                    ctype=ContentType.objects.get_for_model(HomePage),
                ),
                FeedbackPromptPageType(
                    ctype=ContentType.objects.get_for_model(GeneralPage),
                ),
            ],
        )

        self.assertMatchForPath(path, homepage_prompt, page=HomePage(title="Homepage"))
        self.assertMatchForPath(
            path, genericpage_prompt, page=GeneralPage(title="General page")
        )
        self.assertMatchForPath(path, self.default_prompt)
