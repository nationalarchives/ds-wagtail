import json

from django.test import TestCase

from wagtail.core.models import Site

from ..models import InsightsPage


class TestInsightPageSectionBlockIntegration(TestCase):
    def setUp(self):
        root = Site.objects.get().root_page

        self.insights_page = InsightsPage(
            title="Insights page", sub_heading="Introduction"
        )
        self.insights_page.body = json.dumps(
            [
                {
                    "type": "section",
                    "value": {"heading": "Section One"},
                },
                {
                    "type": "section",
                    "value": {"heading": "Section Two"},
                },
            ]
        )
        root.add_child(instance=self.insights_page)

    def test_jumplinks_rendered(self):
        response = self.client.get(self.insights_page.get_url())
        self.assertContains(response, "jumplinks")

    def test_section_one_id(self):
        response = self.client.get(self.insights_page.get_url())
        self.assertContains(response, 'id="section-one"')

    def test_section_one_url(self):
        response = self.client.get(self.insights_page.get_url())
        self.assertContains(response, 'href="#section-one"')

    def test_section_two_id(self):
        response = self.client.get(self.insights_page.get_url())
        self.assertContains(response, 'id="section-two"')

    def test_section_two_url(self):
        response = self.client.get(self.insights_page.get_url())
        self.assertContains(response, 'href="#section-two"')

    def test_jumplinks_not_rendered_if_page_has_no_sections(self):
        self.insights_page.body = json.dumps([])
        self.insights_page.save()

        response = self.client.get(self.insights_page.get_url())
        self.assertNotContains(response, "jumplinks")
