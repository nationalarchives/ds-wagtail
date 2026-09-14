"""
Structural parity tests between the API v2 (DRF-based, custom serializers)
and API v3 (Ninja-based, auto-generated from the same ``api_fields``)
endpoints.

Both APIs are driven by the same ``api_fields`` declared on each page model
(see ``app.api.v3.schemas.register_page_schemas`` and
``wagtail.api.v3.schemas.generators.read``), so for a given page v3 should
include every key exposed by v2, with values of the same JSON type. These
tests don't assert byte-for-byte equality (v2 and v3 legitimately differ in
some details, e.g. numeric precision or key ordering) - they assert that no
field was dropped, renamed, or changed shape (e.g. object -> list) while
migrating from v2 to v3. Fields introduced only in v3 are allowed.

A failure here usually means either:
- a field is missing from one API's ``api_fields`` compared to the other, or
- a custom serializer/schema override needs updating to match the other API.
"""

from datetime import datetime, timezone

from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from app.api.models import APIToken
from app.articles.factories import (
    ArticleIndexPageFactory,
    ArticlePageFactory,
    FocusedArticlePageFactory,
    RecordArticlePageFactory,
)
from app.blog.factories import (
    BlogIndexPageFactory,
    BlogPageFactory,
    BlogPostPageFactory,
)
from app.collections.factories import (
    HighlightGalleryPageFactory,
    TimePeriodPageFactory,
    TopicPageFactory,
)
from app.cookies.factories import CookiesPageFactory
from app.foi.factories import FoiIndexPageFactory
from app.generic_pages.factories import GeneralPageFactory
from app.home.factories import HomePageFactory
from app.people.factories import PeopleIndexPageFactory, PersonPageFactory
from app.whatson.factories import WhatsOnPageFactory

DATE_1 = datetime(2000, 1, 1, tzinfo=timezone.utc)

V2_API_URL = "/api/v2/pages/"
V3_API_URL = "/api/v3/pages/"


class V2V3ApiParityTest(WagtailPageTestCase):
    """
    Compares the API v2 and API v3 detail responses for one page of each
    major page type, asserting every v2 key exists in v3 and has a matching
    value type at every level.
    """

    @classmethod
    def setUpTestData(cls):
        # API v2 uses app-level tokens (DRF TokenAuthentication) and enforces
        # them depending on the WAGTAILAPI_AUTHENTICATION setting, so we
        # authenticate explicitly to make these tests independent of that
        # setting. API v3's page detail endpoint allows anonymous access to
        # live/public pages (authenticating would instead route through the
        # admin-oriented "explorable instances" queryset, which requires
        # Wagtail admin permissions), so it's requested without a token.
        cls.v2_token = APIToken.objects.create(name="test-token")

        cls.root_page = Site.objects.get(is_default_site=True).root_page
        cls.root_page.host_name = "localhost"
        cls.root_page.port = 80
        cls.root_page.save()

        article_index = ArticleIndexPageFactory(
            parent=cls.root_page, title="article_index", first_published_at=DATE_1
        )
        blog_index = BlogIndexPageFactory(
            parent=cls.root_page, title="blog_index", first_published_at=DATE_1
        )
        blog = BlogPageFactory(
            parent=blog_index, title="blog", first_published_at=DATE_1
        )
        people_index = PeopleIndexPageFactory(
            parent=cls.root_page, title="people_index", first_published_at=DATE_1
        )
        foi_index = FoiIndexPageFactory(
            parent=cls.root_page, title="foi_index", first_published_at=DATE_1
        )

        # One representative page per page type, keyed by a human readable
        # label used in subtest output.
        cls.pages = {
            "HomePage": HomePageFactory(
                parent=cls.root_page, title="home", first_published_at=DATE_1
            ),
            "GeneralPage": GeneralPageFactory(
                parent=cls.root_page, title="general", first_published_at=DATE_1
            ),
            "CookiesPage": CookiesPageFactory(
                parent=cls.root_page, title="cookies", first_published_at=DATE_1
            ),
            "ArticleIndexPage": article_index,
            "ArticlePage": ArticlePageFactory(
                parent=article_index,
                title="article",
                first_published_at=DATE_1,
                published_date=DATE_1,
            ),
            "FocusedArticlePage": FocusedArticlePageFactory(
                parent=article_index,
                title="focused_article",
                first_published_at=DATE_1,
                published_date=DATE_1,
            ),
            "RecordArticlePage": RecordArticlePageFactory(
                parent=article_index,
                title="record_article",
                first_published_at=DATE_1,
                published_date=DATE_1,
            ),
            "TopicExplorerPage": TopicPageFactory(
                parent=cls.root_page, title="topic", first_published_at=DATE_1
            ),
            "TimePeriodExplorerPage": TimePeriodPageFactory(
                parent=cls.root_page,
                title="time_period",
                start_year=1485,
                end_year=1714,
                first_published_at=DATE_1,
            ),
            "HighlightGalleryPage": HighlightGalleryPageFactory(
                parent=cls.root_page,
                title="highlight_gallery",
                first_published_at=DATE_1,
            ),
            "PeopleIndexPage": people_index,
            "PersonPage": PersonPageFactory(
                parent=people_index,
                title="person",
                role="Test Author",
                summary="<p>Summary text</p>",
                first_name="John",
                last_name="Smith",
                first_published_at=DATE_1,
            ),
            "BlogIndexPage": blog_index,
            "BlogPage": blog,
            "BlogPostPage": BlogPostPageFactory(
                parent=blog, title="blog_post", first_published_at=DATE_1
            ),
            "WhatsOnPage": WhatsOnPageFactory(
                parent=cls.root_page, title="whats_on", first_published_at=DATE_1
            ),
            "FoiIndexPage": foi_index,
        }

    def get_v2(self, page):
        response = self.client.get(
            f"{V2_API_URL}{page.pk}/",
            format="json",
            HTTP_AUTHORIZATION=f"Token {self.v2_token.key}",
        )
        self.assertEqual(
            response.status_code, 200, f"v2 request failed: {response.content}"
        )
        return response.json()

    def get_v3(self, page):
        response = self.client.get(f"{V3_API_URL}{page.pk}/", format="json")
        self.assertEqual(
            response.status_code, 200, f"v3 request failed: {response.content}"
        )
        return response.json()

    @staticmethod
    def json_type(value) -> str:
        """Return a JSON-schema-style type name for a decoded JSON value."""
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, (int, float)):
            return "number"
        if isinstance(value, str):
            return "string"
        if isinstance(value, list):
            return "array"
        if isinstance(value, dict):
            return "object"
        return "null"

    def assert_structural_parity(self, v2_data: dict, v3_data: dict, path: str = ""):
        """
        Recursively assert that every ``v2_data`` key exists in ``v3_data``,
        and that the value at each v2 key has the same JSON type.

        A `null` value on either side is treated as compatible with anything,
        since a field simply being unset/empty isn't a structural difference.
        """
        v2_keys = set(v2_data.keys())
        v3_keys = set(v3_data.keys())

        self.assertFalse(
            v2_keys - v3_keys,
            f"Missing v2 keys from v3 at '{path or '<root>'}': "
            f"{sorted(v2_keys - v3_keys)}",
        )

        for key in sorted(v2_keys):
            key_path = f"{path}.{key}" if path else key
            v2_value = v2_data[key]
            v3_value = v3_data[key]

            if v2_value is None or v3_value is None:
                continue

            self.assertEqual(
                self.json_type(v2_value),
                self.json_type(v3_value),
                f"Type mismatch at '{key_path}': "
                f"v2={self.json_type(v2_value)} vs v3={self.json_type(v3_value)}",
            )

            if isinstance(v2_value, dict) and isinstance(v3_value, dict):
                self.assert_structural_parity(v2_value, v3_value, key_path)
            elif (
                (isinstance(v2_value, list) and isinstance(v3_value, list))
                and v2_value
                and v3_value
            ):
                v2_item, v3_item = v2_value[0], v3_value[0]
                if isinstance(v2_item, dict) and isinstance(v3_item, dict):
                    self.assert_structural_parity(v2_item, v3_item, f"{key_path}[]")

    def test_structural_parity_for_all_page_types(self):
        for label, page in self.pages.items():
            with self.subTest(page_type=label):
                v2_data = self.get_v2(page)
                v3_data = self.get_v3(page)
                self.assert_structural_parity(v2_data, v3_data)
