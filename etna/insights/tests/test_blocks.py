import json
import re

from django.test import TestCase

from wagtail.core.models import Site

from ..models import InsightsPage


class TestInsightPageSectionBlockIntegration(TestCase):
    def setUp(self):
        root = Site.objects.get().root_page

        self.insights_page = InsightsPage(
            title="Insights page",
            sub_heading="Introduction",
            body=json.dumps(
                [
                    {
                        "type": "content_section",
                        "value": {
                            "heading": "Section One",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "value": {
                                        "text": "<p>This section has two sub-sections. How about that?</p>"
                                    },
                                },
                                {
                                    "type": "sub_heading",
                                    "value": {"heading": "This should render as a h3"},
                                },
                                {
                                    "type": "paragraph",
                                    "value": {
                                        "text": "<p>Some paragraph text following a h3 sub-heading.</p>"
                                    },
                                },
                                {
                                    "type": "content_sub_section",
                                    "value": {
                                        "heading": "Section 1A",
                                        "content": [
                                            {
                                                "type": "paragraph",
                                                "value": {
                                                    "text": "<p>Some paragraph text withing a sub-section.</p>"
                                                },
                                            },
                                            {
                                                "type": "sub_heading",
                                                "value": {
                                                    "heading": "This should render as a h4"
                                                },
                                            },
                                            {
                                                "type": "paragraph",
                                                "value": {
                                                    "text": "<p>Some paragraph text following a h4 sub-heading.</p>"
                                                },
                                            },
                                        ],
                                    },
                                },
                                {
                                    "type": "content_sub_section",
                                    "value": {
                                        "heading": "Section 1B",
                                        "content": [
                                            {
                                                "type": "paragraph",
                                                "value": {
                                                    "text": "<p>Some paragraph text withing another sub-section.</p>"
                                                },
                                            },
                                            {
                                                "type": "sub_heading",
                                                "value": {"heading": "Another h4"},
                                            },
                                            {
                                                "type": "paragraph",
                                                "value": {
                                                    "text": "<p>Some more paragraph text following a h4 sub-heading.</p>"
                                                },
                                            },
                                        ],
                                    },
                                },
                            ],
                        },
                    },
                    {
                        "type": "content_section",
                        "value": {
                            "heading": "Section Two",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "value": {
                                        "text": "<p>Well, this is a terribly sparse section.</p>"
                                    },
                                },
                            ],
                        },
                    },
                ]
            ),
        )
        root.add_child(instance=self.insights_page)

    def test_jumplink_rendering(self):
        response = self.client.get(self.insights_page.get_url())
        self.assertContains(response, "jumplinks")
        self.assertContains(response, 'href="#h2.section-one"')
        self.assertContains(response, 'href="#h2.section-two"')
        self.assertContains(response, 'id="h2.section-one"')
        self.assertContains(response, 'id="h2.section-two"')

    def test_jumplinks_not_rendered_if_page_has_no_sections(self):
        self.insights_page.body = "[]"
        self.insights_page.save()

        response = self.client.get(self.insights_page.get_url())
        self.assertNotContains(response, "jumplinks")

    def assertContainsHeading(
        self, subject: str, heading_text: str, heading_level: int
    ):
        regex = re.compile(
            "<h"
            + str(heading_level)
            + r"[\s\w'\=\-\"\.]*>\s*(.*)\s*<\/h"
            + str(heading_level)
            + ">",
            re.MULTILINE,
        )
        heading_texts = []
        for match in regex.finditer(subject):
            heading_texts.append(match.groups()[0].strip())

        self.assertIn(heading_text, heading_texts)

    def test_headings_rendered_as_h3(self):
        response = self.client.get(self.insights_page.get_url())
        response.render()
        content = response.content.decode()
        for heading_text in (
            "This should render as a h3",
            "Section 1A",
            "Section 1B",
        ):
            with self.subTest(heading_text):
                self.assertContainsHeading(content, heading_text, 3)

    def test_headings_rendered_as_h4(self):
        response = self.client.get(self.insights_page.get_url())
        response.render()
        content = response.content.decode()
        for heading_text in (
            "This should render as a h4",
            "Another h4",
        ):
            with self.subTest(heading_text):
                self.assertContainsHeading(content, heading_text, 4)
