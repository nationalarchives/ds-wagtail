from datetime import timedelta

from django.utils.timezone import localdate
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail_factories import ImageFactory

from app.api.models import APIToken
from app.education.models import (
    EducationPage,
    EducationSessionPage,
    EducationSessionsListingPage,
    TeachingResourcePage,
    TeachingResourcesListingPage,
)
from app.education.models.details import KeyStage, Theme, TimePeriod
from app.education.models.resources import (
    TeachingResourcePageKeyStageTag,
    TeachingResourcePageThemeTag,
    TeachingResourcePageTimePeriodTag,
)
from app.education.models.sessions import (
    EducationSessionPageKeyStageTag,
    EducationSessionPageThemeTag,
    EducationSessionPageTimePeriodTag,
    SessionLocation,
)


class EducationListingsAPITest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.api_token = APIToken.objects.create(name="education-api-token")
        cls.root_page = Site.objects.get(is_default_site=True).root_page

        cls.test_image = ImageFactory()

        cls.ks1, _ = KeyStage.objects.update_or_create(
            slug="key-stage-1",
            defaults={
                "name": "Key stage 1",
                "stage": 1,
                "age_range": "5-7",
            },
        )
        cls.ks3, _ = KeyStage.objects.update_or_create(
            slug="key-stage-3",
            defaults={
                "name": "Key stage 3",
                "stage": 3,
                "age_range": "11-14",
            },
        )
        cls.ks4, _ = KeyStage.objects.update_or_create(
            slug="key-stage-4",
            defaults={
                "name": "Key stage 4",
                "stage": 4,
                "age_range": "14-16",
            },
        )

        cls.early_modern, _ = TimePeriod.objects.update_or_create(
            slug="early-modern",
            defaults={
                "name": "Early modern",
                "year_from": 1485,
                "year_to": 1750,
            },
        )
        cls.early_twentieth_century, _ = TimePeriod.objects.update_or_create(
            slug="early-twentieth-century",
            defaults={
                "name": "Early twentieth century",
                "year_from": 1901,
                "year_to": 1945,
            },
        )

        cls.local_history, _ = Theme.objects.update_or_create(
            slug="local-history",
            defaults={"name": "Local history"},
        )
        cls.medicine_welfare, _ = Theme.objects.update_or_create(
            slug="medicine-welfare-and-society",
            defaults={"name": "Medicine, welfare and society"},
        )

        cls.education_page = cls.publish_page(
            cls.root_page,
            EducationPage(
                title="Education",
                slug="education",
                teaser_text="Education teaser",
                intro="<p>Education landing intro</p>",
                hero_image=cls.test_image,
            ),
        )

        cls.resources_listing_page = cls.publish_page(
            cls.education_page,
            TeachingResourcesListingPage(
                title="Teaching resources",
                slug="teaching-resources",
                teaser_text="Teaching resources teaser",
                intro="<p>Teaching resources intro</p>",
                hero_image=cls.test_image,
            ),
        )

        cls.sessions_listing_page = cls.publish_page(
            cls.education_page,
            EducationSessionsListingPage(
                title="Education sessions",
                slug="education-sessions",
                teaser_text="Education sessions teaser",
                intro="<p>Education sessions intro</p>",
            ),
        )

    @classmethod
    def publish_page(cls, parent_page, page):
        parent_page.add_child(instance=page)
        page.save_revision().publish()
        return page

    def request_api(self, path):
        return self.client.get(
            path,
            format="json",
            HTTP_AUTHORIZATION=f"Token {self.api_token.key}",
        )

    def create_resource_page(self, slug, title, key_stages, time_periods, themes):
        page = TeachingResourcePage(
            title=title,
            slug=slug,
            teaser_text="Resource teaser",
            intro="<p>Resource intro</p>",
            hero_image=self.test_image,
            teachers_notes=[
                {
                    "type": "paragraph",
                    "value": {
                        "text": "<p>Teacher notes</p>",
                    },
                }
            ],
        )

        page.education_keystage_tags = [
            TeachingResourcePageKeyStageTag(key_stage=key_stage)
            for key_stage in key_stages
        ]
        page.education_time_period_tags = [
            TeachingResourcePageTimePeriodTag(time_period=time_period)
            for time_period in time_periods
        ]
        page.education_theme_tags = [
            TeachingResourcePageThemeTag(theme=theme) for theme in themes
        ]

        page = self.publish_page(self.resources_listing_page, page)

        return page

    def create_session_page(
        self,
        slug,
        title,
        key_stages,
        time_periods,
        themes,
        location_types,
        start_date=None,
        end_date=None,
    ):
        page = EducationSessionPage(
            title=title,
            slug=slug,
            teaser_text="Session teaser",
            intro="<p>Session intro</p>",
            hero_image=self.test_image,
            start_date=start_date,
            end_date=end_date,
        )

        page.education_keystage_tags = [
            EducationSessionPageKeyStageTag(key_stage=key_stage)
            for key_stage in key_stages
        ]
        page.education_time_period_tags = [
            EducationSessionPageTimePeriodTag(time_period=time_period)
            for time_period in time_periods
        ]
        page.education_theme_tags = [
            EducationSessionPageThemeTag(theme=theme) for theme in themes
        ]

        location_objects = []
        for location_type in location_types:
            kwargs = {
                "location_type": location_type,
                "duration": "1 hour",
            }
            if location_type == SessionLocation.LocationType.YOUR_SCHOOL:
                kwargs["region"] = SessionLocation.Regions.NORTH_WEST
            location_objects.append(SessionLocation(**kwargs))
        page.session_locations = location_objects

        page = self.publish_page(self.sessions_listing_page, page)

        return page

    def test_resources_endpoint_supports_filters_search_and_pagination(self):
        self.create_resource_page(
            slug="mouse-local-history",
            title="Mouse local history",
            key_stages=[self.ks3],
            time_periods=[self.early_modern],
            themes=[self.local_history],
        )
        self.create_resource_page(
            slug="river-archives",
            title="River archives",
            key_stages=[self.ks4],
            time_periods=[self.early_twentieth_century],
            themes=[self.medicine_welfare],
        )
        self.create_resource_page(
            slug="mouse-medicine",
            title="Mouse and medicine",
            key_stages=[self.ks1, self.ks3],
            time_periods=[self.early_modern],
            themes=[self.medicine_welfare],
        )

        response = self.request_api(
            "/api/v2/education/resources/?key_stage=3&key_stage=1"
            "&time_period=early-modern"
            "&theme=medicine-welfare-and-society"
            "&search=mouse"
        )

        self.assertEqual(response.status_code, 200, response.content.decode())
        response_data = response.json()
        self.assertIn("meta", response_data)
        self.assertIn("items", response_data)
        self.assertIn("total_count", response_data["meta"])

        self.assertEqual(response_data["meta"]["total_count"], 1)
        self.assertEqual(len(response_data["items"]), 1)
        self.assertEqual(response_data["items"][0]["title"], "Mouse and medicine")
        self.assertIn("key_stages", response_data["items"][0])
        self.assertIn("time_periods", response_data["items"][0])
        self.assertIn("themes", response_data["items"][0])

        paginated_response = self.request_api(
            "/api/v2/education/resources/?limit=1&offset=1"
        )
        self.assertEqual(
            paginated_response.status_code,
            200,
            paginated_response.content.decode(),
        )
        paginated_data = paginated_response.json()
        self.assertEqual(paginated_data["meta"]["total_count"], 3)
        self.assertEqual(len(paginated_data["items"]), 1)

    def test_sessions_endpoint_supports_location_taxonomy_search_and_pagination(self):
        future_date = localdate() + timedelta(days=7)
        past_date = localdate() - timedelta(days=7)

        self.create_session_page(
            slug="mouse-online-local",
            title="Mouse online local",
            key_stages=[self.ks3],
            time_periods=[self.early_modern],
            themes=[self.local_history],
            location_types=[SessionLocation.LocationType.ONLINE],
            start_date=future_date,
        )
        self.create_session_page(
            slug="mouse-school-medicine",
            title="Mouse school medicine",
            key_stages=[self.ks1],
            time_periods=[self.early_modern],
            themes=[self.medicine_welfare],
            location_types=[SessionLocation.LocationType.YOUR_SCHOOL],
            start_date=future_date,
        )
        self.create_session_page(
            slug="mouse-at-tna-medicine",
            title="Mouse at TNA medicine",
            key_stages=[self.ks1],
            time_periods=[self.early_modern],
            themes=[self.medicine_welfare],
            location_types=[SessionLocation.LocationType.NATIONAL_ARCHIVES],
            start_date=future_date,
        )
        self.create_session_page(
            slug="mouse-past-medicine",
            title="Mouse past medicine",
            key_stages=[self.ks1],
            time_periods=[self.early_modern],
            themes=[self.medicine_welfare],
            location_types=[SessionLocation.LocationType.ONLINE],
            start_date=past_date,
            end_date=past_date,
        )

        response = self.request_api(
            "/api/v2/education/sessions/?key_stage=1&key_stage=3"
            "&time_period=early-modern"
            "&theme=medicine-welfare-and-society"
            "&location=online&location=your_school"
            "&search=mouse"
        )

        self.assertEqual(response.status_code, 200, response.content.decode())
        response_data = response.json()
        self.assertIn("meta", response_data)
        self.assertIn("items", response_data)
        self.assertIn("total_count", response_data["meta"])

        self.assertEqual(response_data["meta"]["total_count"], 1)
        self.assertEqual(len(response_data["items"]), 1)
        self.assertEqual(response_data["items"][0]["title"], "Mouse school medicine")
        self.assertIn("session_locations", response_data["items"][0])
        self.assertIn("key_stages", response_data["items"][0])
        self.assertIn("time_periods", response_data["items"][0])
        self.assertIn("themes", response_data["items"][0])

        paginated_response = self.request_api(
            "/api/v2/education/sessions/?limit=1&offset=1"
        )
        self.assertEqual(
            paginated_response.status_code,
            200,
            paginated_response.content.decode(),
        )
        paginated_data = paginated_response.json()
        self.assertEqual(paginated_data["meta"]["total_count"], 3)
        self.assertEqual(len(paginated_data["items"]), 1)

        # Past sessions should not be browsable on the sessions endpoint.
        past_session_response = self.request_api(
            "/api/v2/education/sessions/?search=past"
        )
        self.assertEqual(
            past_session_response.status_code,
            200,
            past_session_response.content.decode(),
        )
        self.assertEqual(past_session_response.json()["meta"]["total_count"], 0)

    def test_sessions_endpoint_region_filter_does_not_default_to_national_archives(
        self,
    ):
        future_date = localdate() + timedelta(days=7)

        self.create_session_page(
            slug="mouse-school-north-east",
            title="Mouse school north east",
            key_stages=[self.ks1],
            time_periods=[self.early_modern],
            themes=[self.medicine_welfare],
            location_types=[SessionLocation.LocationType.YOUR_SCHOOL],
            start_date=future_date,
        )
        self.create_session_page(
            slug="mouse-custom-south-west",
            title="Mouse custom south west",
            key_stages=[self.ks1],
            time_periods=[self.early_modern],
            themes=[self.medicine_welfare],
            location_types=[SessionLocation.LocationType.CUSTOM],
            start_date=future_date,
        )
        self.create_session_page(
            slug="mouse-at-tna",
            title="Mouse at TNA",
            key_stages=[self.ks1],
            time_periods=[self.early_modern],
            themes=[self.medicine_welfare],
            location_types=[SessionLocation.LocationType.NATIONAL_ARCHIVES],
            start_date=future_date,
        )

        response = self.request_api(
            "/api/v2/education/sessions/?region=north-east&region=south-west"
        )

        self.assertEqual(response.status_code, 200, response.content.decode())
        response_data = response.json()

        self.assertEqual(response_data["meta"]["total_count"], 2)
        self.assertEqual(
            {item["title"] for item in response_data["items"]},
            {"Mouse school north east", "Mouse custom south west"},
        )

    def test_teaching_resources_listing_page_returns_ordered_search_filters(self):
        self.create_resource_page(
            slug="resources-order-one",
            title="Resources order one",
            key_stages=[self.ks3],
            time_periods=[self.early_twentieth_century],
            themes=[self.medicine_welfare],
        )
        self.create_resource_page(
            slug="resources-order-two",
            title="Resources order two",
            key_stages=[self.ks1],
            time_periods=[self.early_modern],
            themes=[self.local_history],
        )

        response = self.request_api(f"/api/v2/pages/{self.resources_listing_page.id}/")

        self.assertEqual(response.status_code, 200, response.content.decode())
        search_filters = response.json()["search_filters"]

        self.assertEqual(
            [item["stage"] for item in search_filters["key_stage"]],
            [1, 3],
        )
        self.assertEqual(
            [item["slug"] for item in search_filters["time_period"]],
            ["early-modern", "early-twentieth-century"],
        )
        self.assertEqual(
            [item["name"] for item in search_filters["theme"]],
            ["Local history", "Medicine, welfare and society"],
        )

    def test_education_sessions_listing_page_includes_current_or_future_locations(self):
        future_date = localdate() + timedelta(days=3)
        past_date = localdate() - timedelta(days=30)

        self.create_session_page(
            slug="future-online-session",
            title="Future online session",
            key_stages=[self.ks1],
            time_periods=[self.early_modern],
            themes=[self.local_history],
            location_types=[SessionLocation.LocationType.ONLINE],
            start_date=future_date,
            end_date=future_date,
        )
        self.create_session_page(
            slug="past-archive-session",
            title="Past archive session",
            key_stages=[self.ks4],
            time_periods=[self.early_twentieth_century],
            themes=[self.medicine_welfare],
            location_types=[SessionLocation.LocationType.NATIONAL_ARCHIVES],
            start_date=past_date,
            end_date=past_date,
        )

        response = self.request_api(f"/api/v2/pages/{self.sessions_listing_page.id}/")

        self.assertEqual(response.status_code, 200, response.content.decode())
        search_filters = response.json()["search_filters"]

        self.assertEqual(
            [item["slug"] for item in search_filters["location"]],
            ["online"],
        )
        self.assertEqual(
            [item["stage"] for item in search_filters["key_stage"]],
            [1],
        )
        self.assertEqual(
            [item["slug"] for item in search_filters["time_period"]],
            ["early-modern"],
        )
        self.assertEqual(
            [item["slug"] for item in search_filters["theme"]],
            ["local-history"],
        )
