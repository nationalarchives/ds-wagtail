from django.test import TestCase

from etna.feedback.models import FeedbackPrompt


class TestFeedbackPromptGetForPath(TestCase):
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

    def assertMatchForPath(self, path: str, expected_prompt: FeedbackPrompt):
        result = FeedbackPrompt.objects.get_for_path(path)
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
