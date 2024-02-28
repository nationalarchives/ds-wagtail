import json

from django.test import TestCase
from wagtail.models import Site

from ..models import GeneralPage


class TestGeneral(TestCase):
    def setUp(self):
        root = Site.objects.get().root_page

        self.general_page = GeneralPage(
            title="General page",
            teaser_text="test",
            body=json.dumps(
                [
                    {
                        "type": "paragraph",
                        "value": {"text": "This is a paragraph"},
                    },
                ]
            ),
        )
        root.add_child(instance=self.general_page)

    def test_view_uses_correct_template(self):
        url = self.general_page.get_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "generic_pages/general_page.html")
