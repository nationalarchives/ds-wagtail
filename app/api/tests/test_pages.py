import os
import re
from datetime import datetime, timezone
from unittest.mock import patch

from django.conf import settings
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail_factories import ImageFactory

from app.alerts.models import Alert
from app.articles.factories import (
    ArticleIndexPageFactory,
    ArticlePageFactory,
    FocusedArticlePageFactory,
    RecordArticlePageFactory,
)
from app.articles.models import ArticleTag
from app.collections.factories import (
    HighlightGalleryPageFactory,
    TimePeriodPageFactory,
    TopicPageFactory,
)
from app.collections.models import Highlight, PageTimePeriod, PageTopic
from app.home.models import MourningNotice
from app.media.models import EtnaMedia
from app.people.factories import PeopleIndexPageFactory, PersonPageFactory
from app.people.models import AuthorTag, PersonRole, PersonRoleSelection

API_URL = "/api/v2/pages/"

DATE_1 = datetime(2000, 1, 1, tzinfo=timezone.utc)

DATE_2 = datetime(2000, 1, 2, tzinfo=timezone.utc)

DATE_3 = datetime(2000, 1, 3, tzinfo=timezone.utc)

FILE_PATH = os.path.join(os.path.dirname(__file__), "expected_results")


class APIResponseTest(WagtailPageTestCase):
    """
    Test the API responses on the pages endpoint.

    These will likely fail if any of the serializers are changed,
    please update the expected JSON if this is the case.

    If these are failing for any other reason, please investigate
    the cause of the failure further - it may be an issue with one
    of the serializers. Please update the serializer and the expected
    JSON if this is the case, but we should aim to keep the output
    as consistent as possible to avoid breaking changes on the front end.
    """

    @classmethod
    def setUpTestData(self):
        self.root_page = Site.objects.get().root_page
        self.root_page.host_name = "localhost"
        self.root_page.port = 80
        self.root_page.mourning = [
            MourningNotice.objects.create(
                title="Test title",
                message="<p>Test message</p>",
                page=self.root_page,
                page_id=self.root_page.id,
            )
        ]

        self.test_image = ImageFactory(
            transcription="<p>Transcript</p>",
            translation="<p>Translation</p>",
            copyright="Copyrighted by someone",
            description="Some alt text",
        )

        self.alert = Alert.objects.create(
            title="BETA",
            message="<p>Message</p>",
            active=True,
            cascade=True,
            alert_level="high",
        )

        self.test_media = EtnaMedia.objects.create(
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

        self.arts = TopicPageFactory(
            title="arts",
            parent=self.root_page,
            first_published_at=DATE_1,
        )

        self.early_modern = TimePeriodPageFactory(
            title="early_modern",
            start_year=1485,
            end_year=1714,
            parent=self.root_page,
            first_published_at=DATE_1,
        )

        self.postwar = TimePeriodPageFactory(
            title="postwar",
            start_year=1945,
            end_year=2000,
            parent=self.root_page,
            first_published_at=DATE_1,
        )

        self.author_index_page = PeopleIndexPageFactory(
            parent=self.root_page,
            title="people",
            first_published_at=DATE_1,
            alert=self.alert,
        )

        self.author_role = PersonRole(
            name="Author",
            slug="author",
            display_on_card=True,
        )

        self.board_member_role = PersonRole(
            name="Board Member",
            slug="board-member",
            display_on_card=False,
        )

        self.author_page = PersonPageFactory(
            title="author",
            role="Test Author",
            summary="<p>Summary text</p>",
            first_published_at=DATE_1,
            parent=self.author_index_page,
            first_name="John",
            last_name="Smith",
        )

        self.author_role.save()
        self.board_member_role.save()

        self.author_page.roles.add(PersonRoleSelection(role=self.author_role))
        self.author_page.roles.add(PersonRoleSelection(role=self.board_member_role))
        self.author_page.save()

        self.article_index = ArticleIndexPageFactory(
            parent=self.root_page,
            title="article_index",
            first_published_at=DATE_1,
        )

        self.article = ArticlePageFactory(
            parent=self.article_index,
            title="article",
            intro='<p>This is an article with <a linktype="page" id="3">a link to a page</a><page>',
            page_topics=[PageTopic(topic=self.arts)],
            page_time_periods=[
                PageTimePeriod(time_period=self.early_modern),
                PageTimePeriod(time_period=self.postwar),
            ],
            first_published_at=DATE_1,
            published_date=DATE_1,
        )

        self.focused_article = FocusedArticlePageFactory(
            parent=self.article_index,
            title="focused_article",
            page_topics=[PageTopic(topic=self.arts)],
            page_time_periods=[PageTimePeriod(time_period=self.early_modern)],
            author_tags=[AuthorTag(author=self.author_page)],
            first_published_at=DATE_2,
            published_date=DATE_2,
        )

        self.record_article = RecordArticlePageFactory(
            parent=self.article_index,
            title="record_article",
            page_topics=[PageTopic(topic=self.arts)],
            page_time_periods=[PageTimePeriod(time_period=self.early_modern)],
            first_published_at=DATE_3,
            published_date=DATE_3,
        )

        self.BODY_JSON = [
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
                                "image": self.test_image.id,
                                "caption": '<p data-block-key="apto9">Caption text</p>',
                            },
                        },
                        {
                            "id": "6e6816e0-6634-46cc-bf75-0c7d737a4cb2",
                            "type": "media",
                            "value": {
                                "media": self.test_media.id,
                                "title": "Media title",
                                "thumbnail": self.test_image.id,
                            },
                        },
                        {
                            "id": "b505f636-f3d1-4d4b-b368-69183e324e6e",
                            "type": "featured_record_article",
                            "value": {
                                "page": self.record_article.id,
                            },
                        },
                        {
                            "id": "dc5a68fd-17b2-4722-916b-0a924bdb189a",
                            "type": "promoted_list",
                            "value": {
                                "summary": '<p data-block-key="9rpsq">Summary</p>',
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
                                            "thumbnail_image": self.test_image.id,
                                            "descriptive_title": "Record title",
                                        },
                                    }
                                ]
                            },
                        },
                    ],
                    "heading": "Heading text",
                },
            }
        ]

        self.FEATURED_PAGES_JSON = [
            {
                "id": "f3544bb7-11e1-4894-9e9d-02ada7409600",
                "type": "featuredpages",
                "value": {
                    "items": [
                        {
                            "id": "932d1336-7405-4935-bc3b-ddb8610ab9fa",
                            "type": "item",
                            "value": self.article.id,
                        },
                        {
                            "id": "084374fe-1405-47d0-913d-ed90c3a60b69",
                            "type": "item",
                            "value": self.focused_article.id,
                        },
                    ],
                    "heading": "Featured pages heading",
                    "description": "Featured pages description",
                },
            }
        ]

        self.witchcraft = ArticleTag.objects.get(name="Witchcraft")
        self.medicine = ArticleTag.objects.get(name="Medicine")
        self.article.tags.add(self.witchcraft)
        self.article.body = self.BODY_JSON
        self.article.save()

        self.focused_article.tags.add(self.medicine)
        self.focused_article.tags.add(self.witchcraft)
        self.focused_article.save()

        self.article_index.featured_article = self.article
        self.article_index.featured_pages = self.FEATURED_PAGES_JSON
        self.article_index.save()

        self.highlight_gallery = HighlightGalleryPageFactory(
            parent=self.arts,
            title="highlight_gallery",
            featured_article=self.article,
            page_highlights=[
                Highlight(
                    image=self.test_image,
                    record="C123",
                    description="<p>Test description</p>",
                )
            ],
            page_topics=[PageTopic(topic=self.arts)],
            page_time_periods=[PageTimePeriod(time_period=self.early_modern)],
            first_published_at=DATE_3,
        )

    def request_api(self, path: str = ""):
        self.maxDiff = None
        return self.client.get(
            f"{API_URL}{path}" + ("/" if path else ""), format="json"
        )

    def get_api_data(self, path: str = "") -> str:
        if api_response := self.request_api(path):
            if api_response.status_code == 200:
                return api_response.content.decode("utf-8")
            return f"Endpoint not OK (Error: {api_response.status_code})"
        return f"Unable to request endpoint {API_URL}{path}"

    def replace_placeholders(self, data: str):
        placeholder_ids = {
            "HOME_PAGE_ID": str(self.root_page.id),
            "ARTICLE_INDEX_ID": str(self.article_index.id),
            "ARTICLE_ID": str(self.article.id),
            "ALERT_UID": str(self.alert.uid),
            "FOCUSED_ID": str(self.focused_article.id),
            "RECORD_ID": str(self.record_article.id),
            "ARTS_ID": str(self.arts.id),
            "EARLY_MODERN_ID": str(self.early_modern.id),
            "POSTWAR_ID": str(self.postwar.id),
            "AUTHOR_INDEX_ID": str(self.author_index_page.id),
            "AUTHOR_ID": str(self.author_page.id),
            "HIGHLIGHT_GALLERY_ID": str(self.highlight_gallery.id),
            "WAGTAILAPI_BASE_URL": str(settings.WAGTAILAPI_BASE_URL),
        }

        for placeholder, id in placeholder_ids.items():
            data = data.replace(placeholder, id)

        return data

    def compare_json(self, path: str, json_file: str):
        if api_data := self.get_api_data(path):
            if api_data.startswith("Endpoint") or api_data.startswith("Unable"):
                self.fail(api_data)
            else:
                file = os.path.join(FILE_PATH, f"{json_file}.json")
                expected_data = open(file, "r").read()

                # Replace placeholders with actual IDs in JSON
                expected_data = self.replace_placeholders(expected_data)

                # Remove random image rendition IDs
                regex_start = r"/media/images/[a-zA-Z0-9_]+\.([a-fA-F0-9]{6,8}\.)?"
                replace_end = "/media/images/image."
                expected_data = re.sub(regex_start, replace_end, expected_data)
                api_data = re.sub(regex_start, replace_end, api_data)
                regex_end = r"\.format-(jpeg|webp)\.(jpegquality|webpquality)-([0-9]+)[a-zA-Z0-9_]*\.(jpg|webp)"
                regex_replace_end = r".format-\g<1>.\g<2>-\g<3>.\g<4>"
                expected_data = re.sub(regex_end, regex_replace_end, expected_data)
                api_data = re.sub(regex_end, regex_replace_end, api_data)

                # Remove random generated UUIDs from the JSON for images and media
                expected_data = re.sub(
                    r'"uuid": "[a-f0-9\-]+"',
                    '"uuid": "00000000-0000-0000-0000-000000000000"',
                    expected_data,
                )
                api_data = re.sub(
                    r'"uuid": "[a-f0-9\-]+"',
                    '"uuid": "00000000-0000-0000-0000-000000000000"',
                    api_data,
                )

                # Fix the site root domain
                api_data = api_data.replace("https://localhost/", "http://localhost/")

                self.assertEqual(expected_data, api_data)

    def test_pages_route(self):
        self.compare_json("", "pages")

    def test_multiple_page_routes(self):
        for page in (
            self.article,
            self.focused_article,
            self.record_article,
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

    @patch("app.ciim.client.CIIMClient.get")
    def test_record_article_serializer(self, mock_record):
        mock_record.return_value = {
            "data": [
                {
                    "@template": {
                        "details": {
                            "summaryTitle": "Test record title",
                            "iaid": "C4761957",
                            "referenceNumber": "TEST 1/2/3",
                        }
                    }
                }
            ]
        }
        self.compare_json(
            str(self.record_article.id), f"{self.record_article.title}_serialized"
        )
