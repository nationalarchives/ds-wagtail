import json
import re

from django.test import TestCase

from wagtail.core.models import Site

from ..models import AboutPage


class TestAbout(TestCase):
    def setUp(self):
        root = Site.objects.get().root_page

        self.about_page = AboutPage(
            title="About page",
            body=json.dumps(
                [
                    {"type": "paragraph", "value": {"text": "This is a paragraph"}},
                ]
            ),
        )
        root.add_child(instance=self.about_page)

    def assertContainsParagraph(self, subject: str, paragraph_text: str):
        regex = re.compile(
            "<div" + r"[\s\w'\=\-\"\.]*>\s*(.*)\s*<\/div" + ">",
            re.MULTILINE,
        )
        paragraph_texts = []
        for match in regex.finditer(subject):
            paragraph_texts.append(match.groups()[0].strip())

        self.assertIn(paragraph_text, paragraph_texts)

    def test_view_url_accessible_by_name(self):
        url = "/about-page/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        url = self.about_page.get_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about/about_page.html")

    def test_paragraph_rendered_as_div(self):
        url = self.about_page.get_url()
        response = self.client.get(url)
        response.render()
        content = response.content.decode()
        for paragraph_text in ("This is a paragraph",):
            with self.subTest(paragraph_text):
                self.assertContainsParagraph(content, paragraph_text)
