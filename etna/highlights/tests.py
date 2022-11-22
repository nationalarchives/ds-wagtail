import json

from django.test import TestCase

from wagtail.models import Site

from .models import CloserLookPage


class TestCloserLookPageSectionBlockIntegration(TestCase):
    def setUp(self):
        root = Site.objects.get().root_page

        self.closer_look_page = CloserLookPage(
            title="Closer look page",
            body=json.dumps(
                [
                    {
                        "type": "record_info",
                        "value": {
                            "date": "25th March 1616",
                            "record": "F257483",
                            "paragraph": {
                                "text": "<p data-block-key=\"xvzqp\">This is a test for the paragraph text.</p>"
                            }
                        }
                    }
                ]
            ),
        )
        root.add_child(instance=self.closer_look_page)

    def test_paragraph_rendering(self):
        response = self.client.get(self.closer_look_page.get_url())
        self.assertContains(response, "jumplinks")
        self.assertContains(response, 'href="#h2.section-one"')
        self.assertContains(response, 'href="#h2.section-two"')
        self.assertContains(response, 'id="h2.section-one"')
        self.assertContains(response, 'id="h2.section-two"')

    def test_jumplinks_not_rendered_if_page_has_no_sections(self):
        self.closer_look_page.body = "[]"
        self.closer_look_page.save()

        response = self.client.get(self.closer_look_page.get_url())
        self.assertNotContains(response, "jumplinks")

    def test_headings_rendered_as_h3(self):
        response = self.client.get(self.closer_look_page.get_url())
        response.render()
        content = response.content.decode()
        self.assertContainsHeading(content, "This should render as a h3", 3)
