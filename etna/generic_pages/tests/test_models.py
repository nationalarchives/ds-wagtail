import json
import re

from django.test import TestCase

from wagtail.core.models import Site

from ..models import GeneralPage


class TestGeneral(TestCase):
    def setUp(self):
        root = Site.objects.get().root_page

        self.general_page = GeneralPage(
            title="General page",
            body=json.dumps(
                [
                    {"type": "paragraph", "value": {"text": "This is a paragraph"}},
                ]
            ),
        )
        root.add_child(instance=self.general_page)

    def assertContainsParagraph(self, subject: str, paragraph_text: str):
        regex = re.compile(
            "<div" + r"[\s\w'\=\-\"\.]*>\s*(.*)\s*<\/div" + ">",
            re.MULTILINE,
        )
        paragraph_texts = []
        for match in regex.finditer(subject):
            paragraph_texts.append(match.groups()[0].strip())

        self.assertIn(paragraph_text, paragraph_texts)

    def test_view_uses_correct_template(self):
        url = self.general_page.get_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "generic_pages/general_page.html")

    def test_paragraph_rendered_as_div(self):
        url = self.general_page.get_url()
        response = self.client.get(url)
        response.render()
        content = response.content.decode()
        for paragraph_text in ("This is a paragraph",):
            with self.subTest(paragraph_text):
                self.assertContainsParagraph(content, paragraph_text)
