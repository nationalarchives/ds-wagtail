import json

from django.test import TestCase

from wagtail.models import Site

from .models import CloserLookPage


class TestCloserLookPageSectionBlockIntegration(TestCase):
    def setUp(self):
        root = Site.objects.get().root_page

        self.closer_look_page = CloserLookPage(
            title="Test closer look page",
            standfirst = "This is a test to make sure the standfirst is working",
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

    def test_title_rendering(self):
        response = self.client.get(self.closer_look_page.get_url())
        self.assertContains(response, "Test closer look page")