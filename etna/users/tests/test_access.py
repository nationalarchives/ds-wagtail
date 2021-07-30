from django.contrib.auth import get_user_model

User = get_user_model()
from django.contrib.auth.models import Group, Permission
from django.test import TestCase, override_settings

from wagtail.core.models import GroupPagePermission, PageViewRestriction

import responses

from ddt import ddt, data, unpack

from ...ciim.tests.factories import create_record, create_response
from ...collections.models import ExplorerIndexPage, TopicExplorerPage, ResultsPage
from ...home.models import HomePage
from ...insights.models import InsightsIndexPage, InsightsPage


class UserAccessTestCase:
    """Base class used to create accounts for testing whether users can access
    a resource."""

    def setUp(self):
        admin_user = User(
            username="admin@email.com", email="admin@email.com", is_superuser=True
        )
        admin_user.set_password("password")
        admin_user.save()

        moderator = User(username="moderator@email.com", email="moderator@email.com")
        moderator.set_password("password")
        moderator.save()
        moderator.groups.add(Group.objects.get(name="Moderators"))

        editor = User(username="editor@email.com", email="editor@email.com")
        editor.set_password("password")
        editor.save()
        editor.groups.add(Group.objects.get(name="Editors"))

        private_beta_user = User(
            username="private-beta@email.com", email="private-beta@email.com"
        )
        private_beta_user.set_password("password")
        private_beta_user.save()
        private_beta_user.groups.add(Group.objects.get(name="Beta Testers"))


@ddt
class TestHomePage(UserAccessTestCase, TestCase):
    """Ensure that the HomePage is accessible to all.

    This test ensure that a HomePage with no restrictions is accessible.

    It cannot ensure that the HomePage settings in the CMS haven't been
    changed."""

    @unpack
    @data(
        ("admin@email.com", 200),
        ("private-beta@email.com", 200),
        ("moderator@email.com", 200),
        ("editor@email.com", 200),
        (None, 200),
    )
    def test_can_access_home_page(self, email, expected_status_code):
        self.client.login(email=email, password="password")

        response = self.client.get("/")

        self.assertEquals(expected_status_code, response.status_code)


@ddt
class TestInsightsPages(UserAccessTestCase, TestCase):
    """Ensure that the insights page are accessible to the appropriate users.

    This test is to sense-check the appropriate settings. It cannot ensure that
    the settings in the CMS haven't been changed."""

    def setUp(self):
        super().setUp()

        home = HomePage.objects.get()

        insights_index_page = InsightsIndexPage(
            title="Insights Index Page", sub_heading="Sub heading"
        )
        home.add_child(instance=insights_index_page)

        restriction = PageViewRestriction.objects.create(
            page=insights_index_page, restriction_type=PageViewRestriction.GROUPS
        )
        restriction.groups.add(Group.objects.get(name="Beta Testers"))
        restriction.groups.add(Group.objects.get(name="Moderators"))
        restriction.groups.add(Group.objects.get(name="Editors"))

        insights_page = InsightsPage(title="Insights", sub_heading="Sub heading")
        insights_index_page.add_child(instance=insights_page)

    @unpack
    @data(
        ("admin@email.com", 200),
        ("private-beta@email.com", 200),
        ("moderator@email.com", 200),
        ("editor@email.com", 200),
        (None, 302),
    )
    def test_can_access_insights_index_page(self, email, expected_status_code):
        self.client.login(email=email, password="password")

        response = self.client.get("/insights-index-page/")

        self.assertEquals(expected_status_code, response.status_code)

    @unpack
    @data(
        ("admin@email.com", 200),
        ("private-beta@email.com", 200),
        ("moderator@email.com", 200),
        ("editor@email.com", 200),
        (None, 302),
    )
    def test_can_access_insights_page(self, email, expected_status_code):
        self.client.login(email=email, password="password")

        response = self.client.get("/insights-index-page/insights/")

        self.assertEquals(expected_status_code, response.status_code)


@ddt
class TestCollectionsPages(UserAccessTestCase, TestCase):
    """Ensure that the explorer pages are accessible to the appropriate users.

    This test is to sense-check the appropriate settings. It cannot ensure that
    the settings in the CMS haven't been changed."""

    def setUp(self):
        super().setUp()

        home = HomePage.objects.get()

        explorer_index_page = ExplorerIndexPage(
            title="explorer Index Page", sub_heading="Sub heading"
        )
        home.add_child(instance=explorer_index_page)

        restriction = PageViewRestriction.objects.create(
            page=explorer_index_page, restriction_type=PageViewRestriction.GROUPS
        )
        restriction.groups.add(Group.objects.get(name="Beta Testers"))
        restriction.groups.add(Group.objects.get(name="Moderators"))
        restriction.groups.add(Group.objects.get(name="Editors"))

        topic_explorer_page = TopicExplorerPage(
            title="Topic", sub_heading="Sub heading"
        )
        explorer_index_page.add_child(instance=topic_explorer_page)

        results_page = ResultsPage(
            title="results", sub_heading="Sub heading", introduction="Introduction"
        )
        topic_explorer_page.add_child(instance=results_page)

    @unpack
    @data(
        ("admin@email.com", 200),
        ("private-beta@email.com", 200),
        ("moderator@email.com", 200),
        ("editor@email.com", 200),
        (None, 302),
    )
    def test_can_access_explorer_index_page(self, email, expected_status_code):
        self.client.login(email=email, password="password")

        response = self.client.get("/explorer-index-page/")

        self.assertEquals(expected_status_code, response.status_code)

    @unpack
    @data(
        ("admin@email.com", 200),
        ("private-beta@email.com", 200),
        ("moderator@email.com", 200),
        ("editor@email.com", 200),
        (None, 302),
    )
    def test_can_access_explorer_page(self, email, expected_status_code):
        self.client.login(email=email, password="password")

        response = self.client.get("/explorer-index-page/topic/")

        self.assertEquals(expected_status_code, response.status_code)

    @unpack
    @data(
        ("admin@email.com", 200),
        ("private-beta@email.com", 200),
        ("moderator@email.com", 200),
        ("editor@email.com", 200),
        (None, 302),
    )
    def test_can_access_results_page(self, email, expected_status_code):
        self.client.login(email=email, password="password")

        response = self.client.get("/explorer-index-page/topic/results/")

        self.assertEquals(expected_status_code, response.status_code)


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_CLIENT_TEST_MODE=False,
)
@ddt
class TestRecordPageRoutes(UserAccessTestCase, TestCase):
    """Ensure that the record pages are accessible to the appropriate users.

    Unlike similar tests for CMSable pages, these test can assure us that
    routes are only accessible to the appropriate users"""

    @unpack
    @data(
        ("admin@email.com", 200),
        ("private-beta@email.com", 200),
        ("moderator@email.com", 200),
        ("editor@email.com", 200),
        (None, 302),
    )
    @responses.activate
    def test_machine_readable_route(self, email, expected_status_code):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json=create_response(records=[create_record(iaid="c123456")]),
        )

        self.client.login(email=email, password="password")

        response = self.client.get("/catalogue/c123456/")

        self.assertEquals(expected_status_code, response.status_code)

    @unpack
    @data(
        ("admin@email.com", 200),
        ("private-beta@email.com", 200),
        ("moderator@email.com", 200),
        ("editor@email.com", 200),
        (None, 302),
    )
    @responses.activate
    def test_human_readable_route(self, email, expected_status_code):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json=create_response(
                records=[create_record(reference_number="test 1/2/3")]
            ),
        )

        self.client.login(email=email, password="password")

        response = self.client.get("/catalogue/test/1/2/3/")

        self.assertEquals(expected_status_code, response.status_code)


@ddt
class TestImageViewerRoutes(UserAccessTestCase, TestCase):
    """Ensure that the image viewer pages are accessible to the appropriate users.

    Unlike similar tests for CMSable pages, these test can assure us that
    routes are only accessible to the appropriate users"""

    @unpack
    @data(
        ("admin@email.com", 200),
        ("private-beta@email.com", 200),
        ("moderator@email.com", 200),
        ("editor@email.com", 200),
        (None, 302),
    )
    def test_browse_route(self, email, expected_status_code):
        self.client.login(email=email, password="password")

        response = self.client.get("/image-browse/")

        self.assertEquals(expected_status_code, response.status_code)

    @unpack
    @data(
        ("admin@email.com", 200),
        ("private-beta@email.com", 200),
        ("moderator@email.com", 200),
        ("editor@email.com", 200),
        (None, 302),
    )
    def test_viewer_route(self, email, expected_status_code):
        self.client.login(email=email, password="password")

        response = self.client.get("/image-viewer/")

        self.assertEquals(expected_status_code, response.status_code)
