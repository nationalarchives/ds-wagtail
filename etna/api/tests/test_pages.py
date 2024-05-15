from wagtail.models import Site

from wagtail.test.utils import WagtailPageTestCase

from rest_framework.test import APIRequestFactory, APIClient

from wagtail_factories import ImageFactory

from etna.articles.factories import (
    ArticleIndexPageFactory,
    ArticlePageFactory,
    FocusedArticlePageFactory,
)
from etna.authors.factories import AuthorPageFactory
from etna.collections.factories import TimePeriodPageFactory, TopicPageFactory
from etna.collections.models import PageTimePeriod, PageTopic
from etna.authors.models import AuthorTag
from etna.home.factories import HomePageFactory
from etna.media.models import EtnaMedia
from ..urls import PagesAPIViewSet
from django.urls import reverse


class APIResponseTest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = APIRequestFactory()
      

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
        )

        cls.BODY_JSON = []
        
        # [
        #     {
        #         "id": "9da308ae-afea-4177-b200-bd3d50aae884",
        #         "type": "content_section",
        #         "value": {
        #             "content": [
        #                 {
        #                     "id": "f57341a8-1240-4198-a458-902eccef66cd",
        #                     "type": "paragraph",
        #                     "value": {
        #                         "text": '<p data-block-key="5hpue">Here\'s some paragraph text! <b>Bold </b><i>Italic</i></p><ol><li data-block-key="4df22"><i> </i>Numbered list</li></ol><ul><li data-block-key="5d4k9">Bulleted list</li></ul><p data-block-key="ddjmp"><a href="https://google.com">Linked to Google</a></p>'
        #                     },
        #                 },
        #                 {
        #                     "id": "be9a28f4-0067-4922-a6fa-fd118b7c0be9",
        #                     "type": "quote",
        #                     "value": {
        #                         "quote": '<p data-block-key="xhdo0">Quote text</p>',
        #                         "attribution": "John Smith",
        #                     },
        #                 },
        #                 {
        #                     "id": "854cdf5c-c645-4f3b-b5c6-c7920c5a3cd2",
        #                     "type": "sub_heading",
        #                     "value": {"heading": "Sub-heading text"},
        #                 },
        #                 {
        #                     "id": "f5e76e88-7ccb-4802-8b6d-feaf5348c742",
        #                     "type": "image",
        #                     "value": {
        #                         "image": cls.test_image.id,
        #                         "caption": '<p data-block-key="apto9">Caption text</p>',
        #                         "alt_text": "Alt text",
        #                     },
        #                 },
        #                 {
        #                     "id": "6e6816e0-6634-46cc-bf75-0c7d737a4cb2",
        #                     "type": "media",
        #                     "value": {
        #                         "media": cls.test_media.id,
        #                         "title": "Media title",
        #                         "background_image": cls.test_image.id,
        #                     },
        #                 },
        #                 {
        #                     "id": "b505f636-f3d1-4d4b-b368-69183e324e6e",
        #                     "type": "featured_record_article",
        #                     "value": {"page": 3},
        #                 },
        #                 {
        #                     "id": "a48ac0b2-be83-4b01-ae23-4fd1fa525322",
        #                     "type": "promoted_item",
        #                     "value": {
        #                         "url": "https://google.com",
        #                         "image": {
        #                             "image": cls.test_image.id,
        #                             "alt_text": "Image alt text",
        #                             "decorative": False,
        #                         },
        #                         "title": "Title of Featured link",
        #                         "author": "John Smith",
        #                         "category": "blog",
        #                         "duration": "10",
        #                         "cta_label": "CTA Label",
        #                         "description": '<p data-block-key="upl5w">Description</p>',
        #                         "target_blank": True,
        #                         "publication_date": "14 April 2021",
        #                     },
        #                 },
        #                 {
        #                     "id": "dc5a68fd-17b2-4722-916b-0a924bdb189a",
        #                     "type": "promoted_list",
        #                     "value": {
        #                         "summary": '<p data-block-key="9rpsq">Summary</p>',
        #                         "category": 1,
        #                         "promoted_items": [
        #                             {
        #                                 "id": "b244621d-72e4-491a-a168-499e7f3c382c",
        #                                 "type": "item",
        #                                 "value": {
        #                                     "url": "https://google.com",
        #                                     "title": "Promoted title",
        #                                     "description": '<p data-block-key="ig4c0">Promoted description</p>',
        #                                 },
        #                             }
        #                         ],
        #                     },
        #                 },
        #             ],
        #             "heading": "Heading text",
        #         },
        #     }
        # ]

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
            page_time_periods=[PageTimePeriod(time_period=cls.early_modern),PageTimePeriod(time_period=cls.postwar)],
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

    def test_pages_route(self):
      print(self.client.get("/api/v2/pages/", format="json").content.decode("utf-8"))

    def test_article_page_route(self):
      url = f"/api/v2/pages/{self.article.id}/"
      print(self.client.get(url, format="json").content.decode("utf-8"))
       

    # def test_article_page(self):
    #   self.assertEqual(self.article.title, "Article")
    #   self.assertEqual(self.article.intro, "This is an article")
    #   self.assertEqual(self.article.page_topics.first().topic.title, "Arts and culture")
    #   self.assertEqual(
    #       self.article.page_time_periods.first().time_period.title, "Early modern"
    #   )
    #   self.assertPageIsRenderable(self.article)
      
    
    # def test_article_index_page(self):
    #   self.assertPageIsRenderable(self.focused_article)
    #   # response = self.client.get(reverse('/api/v2/pages/'))
    #   # print("CONTENT", response.content)
    #   # print(self.client.get("/api/v2/pages/", format="json").content)
    #   # response = self.factory.request(path="/api/v2/pages/")
    #   # request = self.factory.get("/api/v2/pages/10/")
    #   # print("READ", request.read())
    #   # print("REQUEST", request)
    #   # print("RESPONSE", response)
      




"""
[
  {
    "id": "9da308ae-afea-4177-b200-bd3d50aae884",
    "type": "content_section",
    "value": {
      "content": [
        {
          "id": "f57341a8-1240-4198-a458-902eccef66cd",
          "type": "paragraph",
          "value": {
            "text": "<p data-block-key=\"5hpue\">Here's some paragraph text! <b>Bold </b><i>Italic</i></p><ol><li data-block-key=\"4df22\"><i> </i>Numbered list</li></ol><ul><li data-block-key=\"5d4k9\">Bulleted list</li></ul><p data-block-key=\"ddjmp\"><a href=\"https://google.com\">Linked to Google</a></p>"
          }
        },
        {
          "id": "be9a28f4-0067-4922-a6fa-fd118b7c0be9",
          "type": "quote",
          "value": {
            "quote": "<p data-block-key=\"xhdo0\">Quote text</p>",
            "attribution": "John Smith"
          }
        },
        {
          "id": "854cdf5c-c645-4f3b-b5c6-c7920c5a3cd2",
          "type": "sub_heading",
          "value": {
            "heading": "Sub-heading text"
          }
        },
        {
          "id": "f5e76e88-7ccb-4802-8b6d-feaf5348c742",
          "type": "image",
          "value": {
            "image": 1648,
            "caption": "<p data-block-key=\"apto9\">Caption text</p>",
            "alt_text": "Alt text"
          }
        },
        {
          "id": "6e6816e0-6634-46cc-bf75-0c7d737a4cb2",
          "type": "media",
          "value": {
            "media": 11,
            "title": "Media title",
            "background_image": 1648
          }
        },
        {
          "id": "b505f636-f3d1-4d4b-b368-69183e324e6e",
          "type": "featured_record_article",
          "value": {
            "page": 214
          }
        },
        {
          "id": "a48ac0b2-be83-4b01-ae23-4fd1fa525322",
          "type": "promoted_item",
          "value": {
            "url": "https://google.com",
            "image": {
              "image": 1647,
              "alt_text": "Image alt text",
              "decorative": false
            },
            "title": "Title of Featured link",
            "author": "John Smith",
            "category": "blog",
            "duration": "10",
            "cta_label": "CTA Label",
            "description": "<p data-block-key=\"upl5w\">Description</p>",
            "target_blank": true,
            "publication_date": "14 April 2021"
          }
        },
        {
          "id": "dc5a68fd-17b2-4722-916b-0a924bdb189a",
          "type": "promoted_list",
          "value": {
            "summary": "<p data-block-key=\"9rpsq\">Summary</p>",
            "category": 1,
            "promoted_items": [
              {
                "id": "b244621d-72e4-491a-a168-499e7f3c382c",
                "type": "item",
                "value": {
                  "url": "https://google.com",
                  "title": "Promoted title",
                  "description": "<p data-block-key=\"ig4c0\">Promoted description</p>"
                }
              }
            ]
          }
        },
        {
          "id": "48f967ae-4cc6-4f13-bb12-6c648e747ec3",
          "type": "record_links",
          "value": {
            "items": [
              {
                "id": "acacaa55-924f-4594-bc0b-9f5cb2303ea9",
                "type": "item",
                "value": {
                  "record": "D7376859",
                  "record_dates": "12 April 2021",
                  "thumbnail_image": 1648,
                  "descriptive_title": "Record title"
                }
              }
            ]
          }
        }
      ],
      "heading": "Heading text"
    }
  }
]

"""
