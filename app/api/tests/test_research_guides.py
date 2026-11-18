from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from app.api.models import APIToken
from app.research.models import RelatedRecord, ResearchGuide


class ResearchGuideRecordFilterTests(WagtailPageTestCase):
    def setUp(self):
        self.api_token = APIToken.objects.create(name="test-token")
        self.root_page = Site.objects.get(is_default_site=True).root_page

    def create_research_guide(self, title, record):
        guide = self.root_page.add_child(
            instance=ResearchGuide(
                title=title,
                slug=title.lower().replace(" ", "-"),
                teaser_text="Test guide",
            )
        )
        guide.save_revision().publish()
        RelatedRecord.objects.create(page=guide, record=record)
        return guide

    def test_orders_guides_by_record_specificity(self):
        self.create_research_guide("Ancestor guide", "C1234")
        self.create_research_guide("Exact guide", "C12345")
        self.create_research_guide("Root guide", "C123")
        self.create_research_guide("Another exact guide", "C12345")

        response = self.client.get(
            "/api/v2/research_guides/?record=C12345&ancestor=C1234&ancestor=C123",
            HTTP_AUTHORIZATION=f"Token {self.api_token.key}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["title"] for item in response.json()["items"]],
            [
                "Exact guide",
                "Another exact guide",
                "Ancestor guide",
                "Root guide",
            ],
        )

    def test_rejects_multiple_record_parameters(self):
        response = self.client.get(
            "/api/v2/research_guides/?record=C12345&record=C1234",
            HTTP_AUTHORIZATION=f"Token {self.api_token.key}",
        )

        self.assertEqual(response.status_code, 400)
