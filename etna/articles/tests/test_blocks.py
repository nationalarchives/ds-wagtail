import json
import re

from django.test import TestCase
from wagtail.models import Site

from ..models import ArticlePage


class TestArticlePageSectionBlockIntegration(TestCase):
    def setUp(self):
        root = Site.objects.get().root_page

        self.article_page = ArticlePage(
            title="Article page",
            intro="test",
            teaser_text="test",
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
                                {
                                    "type": "sub_heading",
                                    "value": {"heading": "This should render as a h3"},
                                },
                            ],
                        },
                    },
                ]
            ),
        )
        root.add_child(instance=self.article_page)

    def test_jumplink_rendering(self):
        response = self.client.get(self.article_page.get_url())
        self.assertContains(response, "jumplinks")
        self.assertContains(response, 'href="#h2.section-one"')
        self.assertContains(response, 'href="#h2.section-two"')
        self.assertContains(response, 'id="h2.section-one"')
        self.assertContains(response, 'id="h2.section-two"')

    def test_jumplinks_not_rendered_if_page_has_no_sections(self):
        self.article_page.body = "[]"
        self.article_page.save()

        response = self.client.get(self.article_page.get_url())
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
        response = self.client.get(self.article_page.get_url())
        response.render()
        content = response.content.decode()
        self.assertContainsHeading(content, "This should render as a h3", 3)
