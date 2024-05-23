import os
import re

from datetime import datetime, timezone

from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from wagtail_factories import ImageFactory

from etna.articles.factories import (  # RecordArticlePageFactory,
    ArticleIndexPageFactory,
    ArticlePageFactory,
    FocusedArticlePageFactory,
)
from etna.articles.models import ArticleTag
from etna.authors.factories import AuthorIndexPageFactory, AuthorPageFactory
from etna.authors.models import AuthorTag
from etna.collections.factories import (
    HighlightGalleryPageFactory,
    TimePeriodPageFactory,
    TopicPageFactory,
)
from etna.collections.models import Highlight, PageTimePeriod, PageTopic
from etna.media.models import EtnaMedia

API_URL = "/api/v2/pages/"

DATE_1 = datetime(2000, 1, 1, tzinfo=timezone.utc)

DATE_2 = datetime(2000, 1, 2, tzinfo=timezone.utc)

DATE_3 = datetime(2000, 1, 3, tzinfo=timezone.utc)

FILE_PATH = os.path.join(os.path.dirname(__file__), "expected_results")


class APIResponseTest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_page = Site.objects.get().root_page

        cls.test_image = ImageFactory(
            transcription="<p>Transcript</p>",
            translation="<p>Translation</p>",
            copyright="Copyrighted by someone",
            description="<p>Description</p>",
            record_dates="1900-2000",
        )

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

        cls.arts = TopicPageFactory(
            title="arts",
            parent=cls.root_page,
            first_published_at=DATE_1,
        )

        cls.early_modern = TimePeriodPageFactory(
            title="early_modern",
            start_year=1485,
            end_year=1714,
            parent=cls.root_page,
            first_published_at=DATE_1,
        )

        cls.postwar = TimePeriodPageFactory(
            title="postwar",
            start_year=1945,
            end_year=2000,
            parent=cls.root_page,
            first_published_at=DATE_1,
        )

        cls.author_index_page = AuthorIndexPageFactory(
            parent=cls.root_page,
            title="authors",
            first_published_at=DATE_1,
        )

        cls.author_page = AuthorPageFactory(
            title="author",
            role="Test Author",
            summary="<p>Summary text</p>",
            first_published_at=DATE_1,
            parent=cls.author_index_page,
        )

        cls.article_index = ArticleIndexPageFactory(
            parent=cls.root_page,
            title="article_index",
            first_published_at=DATE_1,
        )

        cls.article = ArticlePageFactory(
            parent=cls.article_index,
            title="article",
            intro='<p>This is an article with <a linktype="page" id="3">a link to a page</a><page>',
            page_topics=[PageTopic(topic=cls.arts)],
            page_time_periods=[
                PageTimePeriod(time_period=cls.early_modern),
                PageTimePeriod(time_period=cls.postwar),
            ],
            first_published_at=DATE_1,
            newly_published_at=DATE_1,
            mark_new_on_next_publish=False,
        )

        cls.focused_article = FocusedArticlePageFactory(
            parent=cls.article_index,
            title="focused_article",
            page_topics=[PageTopic(topic=cls.arts)],
            page_time_periods=[PageTimePeriod(time_period=cls.early_modern)],
            author_tags=[AuthorTag(author=cls.author_page)],
            first_published_at=DATE_2,
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
                            "value": {
                                "page": 3
                            },  # TODO: Set to cls.record_article.id when we can serialize records
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
                                "description": '<p data-block-key="upl5w">Description with <a linktype="page" id="3">a link to a page</a></p>',
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

        cls.FEATURED_PAGES_JSON = [
            {
                "id": "f3544bb7-11e1-4894-9e9d-02ada7409600",
                "type": "featuredpages",
                "value": {
                    "items": [
                        {
                            "id": "932d1336-7405-4935-bc3b-ddb8610ab9fa",
                            "type": "item",
                            "value": cls.article.id,
                        },
                        {
                            "id": "084374fe-1405-47d0-913d-ed90c3a60b69",
                            "type": "item",
                            "value": cls.focused_article.id,
                        },
                    ],
                    "heading": "Featured pages heading",
                    "description": "Featured pages description",
                },
            }
        ]

        cls.witchcraft = ArticleTag.objects.get(name="Witchcraft")
        cls.medicine = ArticleTag.objects.get(name="Medicine")
        cls.article.tags.add(cls.witchcraft)
        cls.article.body = cls.BODY_JSON
        cls.article.save()

        cls.focused_article.tags.add(cls.witchcraft)
        cls.focused_article.tags.add(cls.medicine)
        cls.focused_article.save()

        cls.article_index.featured_article = cls.article
        cls.article_index.featured_pages = cls.FEATURED_PAGES_JSON
        cls.article_index.save()

        # cls.record_article = RecordArticlePageFactory(
        #     parent=cls.article_index,
        #     title="record_article",
        #     page_topics=[PageTopic(topic=cls.arts)],
        #     page_time_periods=[PageTimePeriod(time_period=cls.early_modern)],
        #     first_published_at=DEFAULT_DATE,
        # ) TODO: Uncomment when we can serialize records

        cls.highlight_gallery = HighlightGalleryPageFactory(
            parent=cls.arts,
            title="highlight_gallery",
            featured_article=cls.article,
            page_highlights=[Highlight(image=cls.test_image, alt_text="Alt text")],
            page_topics=[PageTopic(topic=cls.arts)],
            page_time_periods=[PageTimePeriod(time_period=cls.early_modern)],
            first_published_at=DATE_3,
        )

    def request_api(self, path: str = ""):
        return self.client.get(
            f"{API_URL}{path}" + ("/" if path else ""), format="json"
        )

    def get_api_data(self, path: str = "") -> str:
        if api_response := self.request_api(path):
            if api_response.status_code == 200:
                return api_response.content.decode("utf-8")
            return f"Endpoint not OK (Error: {api_response.status_code})"
        return f"Unable to request endpoint {API_URL}{path}"

    def compare_json(self, path: str, json_file: str):
        self.maxDiff = None

        if api_data := self.get_api_data(path):
            if api_data.startswith("Endpoint") or api_data.startswith("Unable"):
                self.fail(api_data)
            else:
                file = os.path.join(FILE_PATH, f"{json_file}.json")
                expected_data = open(file, "r").read()
                expected_data = self.replace_placeholders(expected_data)

                # Remove random image rendition IDs
                expected_data = re.sub(r"0_[a-zA-Z0-9]{7}", "0", expected_data)
                api_data = re.sub(r"0_[a-zA-Z0-9]{7}", "0", api_data)
                expected_data = re.sub(r"e_[a-zA-Z0-9]{7}", "e", expected_data)
                api_data = re.sub(r"e_[a-zA-Z0-9]{7}", "e", api_data)

                self.assertEqual(expected_data, api_data)

    def replace_placeholders(self, data: str):
        placeholder_ids = {
            "HOME_PAGE_ID": str(self.root_page.id),
            "ARTICLE_INDEX_ID": str(self.article_index.id),
            "ARTICLE_ID": str(self.article.id),
            "FOCUSED_ID": str(self.focused_article.id),
            "ARTS_ID": str(self.arts.id),
            "EARLY_MODERN_ID": str(self.early_modern.id),
            "POSTWAR_ID": str(self.postwar.id),
            "AUTHOR_INDEX_ID": str(self.author_index_page.id),
            "AUTHOR_ID": str(self.author_page.id),
            "HIGHLIGHT_GALLERY_ID": str(self.highlight_gallery.id),
        }

        for placeholder, id in placeholder_ids.items():
            data = data.replace(placeholder, id)

        return data

    # def test_output(self):
    #     pages = [self.author_page]
    #     for page in pages:
    #         if api_data := self.get_api_data(str(page.id)):
    #             print(page.title +"\n" + api_data)

    # delete when done ^

    def test_pages_route(self):
        self.maxDiff = None
        self.compare_json("", "pages")

    def test_multiple_page_routes(self):
        for page in (
            self.article,
            self.focused_article,
            self.postwar,
            self.arts,
            self.early_modern,
            self.author_page,
            self.author_index_page,
            self.article_index,
            self.highlight_gallery,
        ):
            with self.subTest(page.title):
                self.compare_json(str(page.id), page.title)
