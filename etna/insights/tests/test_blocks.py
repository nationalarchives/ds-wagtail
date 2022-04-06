import json

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
                        "value": {"heading": "Section One", "content": []},
                    },
                    {
                        "type": "content_section",
                        "value": {"heading": "Section Two", "content": []},
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
