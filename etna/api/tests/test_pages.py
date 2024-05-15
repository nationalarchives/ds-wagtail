from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from wagtail_factories import ImageFactory

from etna.articles.factories import (
    ArticleIndexPageFactory,
    ArticlePageFactory,
    FocusedArticlePageFactory,
)
from etna.authors.factories import AuthorPageFactory
from etna.authors.models import AuthorTag
from etna.collections.factories import TimePeriodPageFactory, TopicPageFactory
from etna.collections.models import PageTimePeriod, PageTopic
from etna.home.factories import HomePageFactory
from etna.media.models import EtnaMedia

from datetime import datetime

API_URL = "/api/v2/pages/"

class APIResponseTest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_page = Site.objects.get().root_page

        cls.test_image = ImageFactory()

        cls.test_media = EtnaMedia.objects.create(
            title="Test media",
            file="media/test.mp4",
            type="video",
            duration=10,
            width=1920,
            height=1080,
            thumbnail="media/test.jpg",
            description="<p>Description</p>",
            transcript="<p>Transcript</p>",
        )

        cls.BODY_JSON = [
            {
                "id": "9da308ae-afea-4177-b200-bd3d50aae884",
                "type": "content_section",
                "value": {
                    "content": [
                        {
                            "id": "f57341a8-1240-4198-a458-902eccef66cd",
                            "type": "paragraph",
                            "value": {
                                "text": '<p data-block-key="5hpue">Here\'s some paragraph text! <b>Bold </b><i>Italic</i></p><ol><li data-block-key="4df22"><i> </i>Numbered list</li></ol><ul><li data-block-key="5d4k9">Bulleted list</li></ul><p data-block-key="ddjmp"><a href="https://google.com">Linked to Google</a></p>'
                            },
                        },
                        {
                            "id": "be9a28f4-0067-4922-a6fa-fd118b7c0be9",
                            "type": "quote",
                            "value": {
                                "quote": '<p data-block-key="xhdo0">Quote text</p>',
                                "attribution": "John Smith",
                            },
                        },
                        {
                            "id": "854cdf5c-c645-4f3b-b5c6-c7920c5a3cd2",
                            "type": "sub_heading",
                            "value": {"heading": "Sub-heading text"},
                        },
                        {
                            "id": "f5e76e88-7ccb-4802-8b6d-feaf5348c742",
                            "type": "image",
                            "value": {
                                "image": cls.test_image.id,
                                "caption": '<p data-block-key="apto9">Caption text</p>',
                                "alt_text": "Alt text",
                            },
                        },
                        {
                            "id": "6e6816e0-6634-46cc-bf75-0c7d737a4cb2",
                            "type": "media",
                            "value": {
                                "media": cls.test_media.id,
                                "title": "Media title",
                                "background_image": cls.test_image.id,
                            },
                        },
                        {
                            "id": "b505f636-f3d1-4d4b-b368-69183e324e6e",
                            "type": "featured_record_article",
                            "value": {"page": 3},
                        },
                        {
                            "id": "a48ac0b2-be83-4b01-ae23-4fd1fa525322",
                            "type": "promoted_item",
                            "value": {
                                "url": "https://google.com",
                                "image": {
                                    "image": cls.test_image.id,
                                    "alt_text": "Image alt text",
                                    "decorative": False,
                                },
                                "title": "Title of Featured link",
                                "author": "John Smith",
                                "category": "blog",
                                "duration": "10",
                                "cta_label": "CTA Label",
                                "description": '<p data-block-key="upl5w">Description</p>',
                                "target_blank": True,
                                "publication_date": "14 April 2021",
                            },
                        },
                        {
                            "id": "dc5a68fd-17b2-4722-916b-0a924bdb189a",
                            "type": "promoted_list",
                            "value": {
                                "summary": '<p data-block-key="9rpsq">Summary</p>',
                                "category": 1,
                                "promoted_items": [
                                    {
                                        "id": "b244621d-72e4-491a-a168-499e7f3c382c",
                                        "type": "item",
                                        "value": {
                                            "url": "https://google.com",
                                            "title": "Promoted title",
                                            "description": '<p data-block-key="ig4c0">Promoted description</p>',
                                        },
                                    }
                                ],
                            },
                        },
                    # { TODO: Uncomment when we can serialize records
                    #   "id": "48f967ae-4cc6-4f13-bb12-6c648e747ec3",
                    #   "type": "record_links",
                    #   "value": {
                    #     "items": [
                    #       {
                    #         "id": "acacaa55-924f-4594-bc0b-9f5cb2303ea9",
                    #         "type": "item",
                    #         "value": {
                    #           "record": "D7376859",
                    #           "record_dates": "12 April 2021",
                    #           "thumbnail_image": cls.test_image.id,
                    #           "descriptive_title": "Record title"
                    #         }
                    #       }
                    #     ]
                    #   }
                    # }
                  ],
                  "heading": "Heading text",
                },
            }
        ]

        cls.homepage = HomePageFactory(parent=cls.root_page)

        cls.article_index = ArticleIndexPageFactory(parent=cls.homepage)

        cls.arts = TopicPageFactory(title="Arts and culture", parent=cls.homepage)

        cls.early_modern = TimePeriodPageFactory(
            title="Early modern", start_year=1485, end_year=1714, parent=cls.homepage
        )

        cls.postwar = TimePeriodPageFactory(
            title="Post war", start_year=1945, end_year=2000, parent=cls.homepage
        )

        cls.article = ArticlePageFactory(
            parent=cls.article_index,
            title="Article",
            intro="This is an article",
            body=cls.BODY_JSON,
            page_topics=[PageTopic(topic=cls.arts)],
            page_time_periods=[
                PageTimePeriod(time_period=cls.early_modern),
                PageTimePeriod(time_period=cls.postwar),
            ],
            first_published_at=datetime()
        )

        cls.author_page = AuthorPageFactory(
            title="John Doe",
            role="Test Author",
            summary="<p>Summary text</p>",
        )

        cls.focused_article = FocusedArticlePageFactory(
            parent=cls.article_index,
            title="Focused article",
            page_topics=[PageTopic(topic=cls.arts)],
            page_time_periods=[PageTimePeriod(time_period=cls.early_modern)],
            author_tags=[AuthorTag(author=cls.author_page)],
        )

    def request_api(self, path=""):
        return self.client.get(f"{API_URL}{path}" + ("/" if path else ""), format="json")
    
    def get_api_data(self, path=""):
        if api_response := self.request_api(path):
          if api_response.status_code == 200:
            return api_response.content.decode("utf-8")
          return f"Endpoint not OK (Error: {api_response.status_code})"
        return f"Unable to request endpoint {API_URL}{path}"

    def test_pages_route(self):
        if api_data := self.get_api_data():
          print("complete")

    def test_multiple_page_routes(self):
        for page in (self.article, self.focused_article, self.postwar, self.arts, self.early_modern):
            with self.subTest(page.title):
                if api_data := self.get_api_data(str(page.id)):
                    print("complete")
