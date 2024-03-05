import unittest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from wagtail.test.utils import WagtailTestUtils

import responses

from etna.core.test_utils import prevent_request_warnings
from etna.records.views.records import SEARCH_URL_RETAIN_DELTA

from ...ciim.tests.factories import create_record, create_response

User = get_user_model()


@unittest.skip("TODO:Rosetta")
class TestRecordDisambiguationView(TestCase):
    @responses.activate
    @prevent_request_warnings
    def test_no_matches_respond_with_404(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/searchUnified",
            json=create_response(records=[]),
        )

        response = self.client.get("/catalogue/ref/AD/2/2/")

        self.assertEqual(
            response.resolver_match.view_name, "details-page-human-readable"
        )
        self.assertEqual(response.status_code, 404)

    @responses.activate
    def test_disambiguation_page_rendered_for_multiple_results(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/searchUnified",
            json=create_response(
                records=[
                    create_record(reference_number="ADM 223/3"),
                    create_record(reference_number="ADM 223/3"),
                ]
            ),
        )

        response = self.client.get("/catalogue/ref/ADM/223/3/")

        self.assertEqual(
            response.resolver_match.view_name, "details-page-human-readable"
        )
        self.assertTemplateUsed(response, "records/record_disambiguation_page.html")

    @responses.activate
    def test_rendering_deferred_to_details_page_view(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/searchUnified",
            json=create_response(
                records=[
                    create_record(iaid="C123456", reference_number="ADM 223/3"),
                ]
            ),
        )

        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(
                records=[
                    create_record(iaid="C123456", reference_number="ADM 223/3"),
                ]
            ),
        )

        response = self.client.get("/catalogue/ref/ADM/223/3/", follow=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.view_name, "details-page-human-readable"
        )
        self.assertTemplateUsed(response, "records/record_detail.html")


class TestRecordView(TestCase):
    @responses.activate
    @prevent_request_warnings
    def test_no_matches_respond_with_404(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(status_code=404),
        )

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.resolver_match.view_name, "details-page-machine-readable"
        )

    @responses.activate
    def test_record_rendered_for_single_result(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(record=create_record(iaid="C123456")),
        )

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.view_name, "details-page-machine-readable"
        )
        self.assertTemplateUsed(response, "records/record_detail.html")

    @responses.activate
    def test_community_record_rendered(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(record=create_record(group="community")),
        )

        response = self.client.get("/catalogue/id/pcw-12345/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.view_name, "details-page-machine-readable"
        )
        self.assertTemplateUsed(response, "records/record_detail.html")


@unittest.skip("TODO:Rosetta")
class TestDataLayerRecordDetail(WagtailTestUtils, TestCase):
    @responses.activate
    def test_datalayer_level1(self):
        import json

        path = f"{settings.BASE_DIR}/etna/records/tests/fixtures/record_level1.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                f"{settings.CLIENT_BASE_URL}/get",
                json=json.loads(f.read()),
            )

        response = self.client.get("/catalogue/id/C241/")

        self.assertTemplateUsed(response, "records/record_detail.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Catalogue: The National Archives", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "record detail", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "", "customDimension9": "", "customDimension10": "", "customDimension11": "Held by not available", "customDimension12": "Level 1 - Lettercode", "customDimension13": "", "customDimension14": "RAIL - Records of the pre-nationalisation railway companies, pre-nationalisation canal and...", "customDimension15": "CAT", "customDimension16": "", "customDimension17": ""}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_level2(self):
        import json

        path = f"{settings.BASE_DIR}/etna/records/tests/fixtures/record_level2.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                f"{settings.CLIENT_BASE_URL}/get",
                json=json.loads(f.read()),
            )

        response = self.client.get("/catalogue/id/C995/")

        self.assertTemplateUsed(response, "records/record_detail.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Catalogue: The National Archives", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "record detail", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "", "customDimension9": "", "customDimension10": "", "customDimension11": "Held by not available", "customDimension12": "Level 2 - Division", "customDimension13": "", "customDimension14": "Division within POWE - Records of the Coal Division", "customDimension15": "CAT", "customDimension16": "", "customDimension17": ""}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_level3(self):
        import json

        path = f"{settings.BASE_DIR}/etna/records/tests/fixtures/record_level3.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                f"{settings.CLIENT_BASE_URL}/get",
                json=json.loads(f.read()),
            )

        response = self.client.get("/catalogue/id/C12441/")

        self.assertTemplateUsed(response, "records/record_detail.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Catalogue: The National Archives", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "record detail", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "", "customDimension9": "", "customDimension10": "", "customDimension11": "66 - The National Archives", "customDimension12": "Level 3 - Series", "customDimension13": "", "customDimension14": "RAIL 253 - Great Western Railway Company: Miscellaneous Books and Records", "customDimension15": "CAT", "customDimension16": "", "customDimension17": ""}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_level4(self):
        import json

        path = f"{settings.BASE_DIR}/etna/records/tests/fixtures/record_level4.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                f"{settings.CLIENT_BASE_URL}/get",
                json=json.loads(f.read()),
            )

        response = self.client.get("/catalogue/id/C31931/")

        self.assertTemplateUsed(response, "records/record_detail.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Catalogue: The National Archives", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "record detail", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "", "customDimension9": "", "customDimension10": "", "customDimension11": "Held by not available", "customDimension12": "Level 4 - Sub-series", "customDimension13": "", "customDimension14": "Sub-series within ADM 171 - AFRICA GENERAL SERVICE MEDAL 1902-1910", "customDimension15": "CAT", "customDimension16": "", "customDimension17": ""}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_level5(self):
        import json

        path = f"{settings.BASE_DIR}/etna/records/tests/fixtures/record_level5.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                f"{settings.CLIENT_BASE_URL}/get",
                json=json.loads(f.read()),
            )

        response = self.client.get("/catalogue/id/C145033/")

        self.assertTemplateUsed(response, "records/record_detail.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Catalogue: The National Archives", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "record detail", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "", "customDimension9": "", "customDimension10": "", "customDimension11": "Held by not available", "customDimension12": "Level 5 - Sub-sub-series", "customDimension13": "IR 900 - Specimens of Series of Documents Destroyed", "customDimension14": "Sub-sub-series within IR 900 - Camden Town Tax District", "customDimension15": "CAT", "customDimension16": "", "customDimension17": ""}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_level6_nondigital(self):
        import json

        path = f"{settings.BASE_DIR}/etna/records/tests/fixtures/record_level6_nondigital.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                f"{settings.CLIENT_BASE_URL}/get",
                json=json.loads(f.read()),
            )

        response = self.client.get("/catalogue/id/C2361422/")

        self.assertTemplateUsed(response, "records/record_detail.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Catalogue: The National Archives", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "record detail", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "", "customDimension9": "", "customDimension10": "", "customDimension11": "66 - The National Archives", "customDimension12": "Level 6 - Piece", "customDimension13": "RAIL 253 - Great Western Railway Company: Miscellaneous Books and Records", "customDimension14": "RAIL 253/516 - Correspondence by members of Audit Office, Paddington while on active service to...", "customDimension15": "CAT", "customDimension16": "", "customDimension17": "No availability condition provisioned for this record"}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_level6_digital(self):
        import json

        path = f"{settings.BASE_DIR}/etna/records/tests/fixtures/record_level6_digital.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                f"{settings.CLIENT_BASE_URL}/get",
                json=json.loads(f.read()),
            )

        response = self.client.get("/catalogue/id/C198022/")

        self.assertTemplateUsed(response, "records/record_detail.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Catalogue: The National Archives", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "record detail", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "", "customDimension9": "", "customDimension10": "", "customDimension11": "66 - The National Archives", "customDimension12": "Level 6 - Piece", "customDimension13": "PROB 1 - Prerogative Court of Canterbury: Wills of Selected Famous Persons", "customDimension14": "PROB 1/4 - Will of William Shakespeare 25 March 1616. Proved 22 June 1616.", "customDimension15": "CAT", "customDimension16": "", "customDimension17": "No availability condition provisioned for this record"}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_level7_nondigital(self):
        import json

        path = f"{settings.BASE_DIR}/etna/records/tests/fixtures/record_level7_nondigital.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                f"{settings.CLIENT_BASE_URL}/get",
                json=json.loads(f.read()),
            )

        response = self.client.get("/catalogue/id/C6518465/")

        self.assertTemplateUsed(response, "records/record_detail.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Catalogue: The National Archives", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "record detail", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "", "customDimension9": "", "customDimension10": "", "customDimension11": "66 - The National Archives", "customDimension12": "Level 7 - Item", "customDimension13": "DSIR 27 - Department of Scientific and Industrial Research: Road Research Laboratory Reports", "customDimension14": "DSIR 27/6/ADM171 - The pressures produced by explosions underwater of 1-oz. solid cone charges of P.E....", "customDimension15": "CAT", "customDimension16": "", "customDimension17": "No availability condition provisioned for this record"}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_level7_digital(self):
        import json

        path = f"{settings.BASE_DIR}/etna/records/tests/fixtures/record_level7_digital.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                f"{settings.CLIENT_BASE_URL}/get",
                json=json.loads(f.read()),
            )

        response = self.client.get("/catalogue/id/C14017032/")

        self.assertTemplateUsed(response, "records/record_detail.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Catalogue: The National Archives", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "record detail", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "", "customDimension9": "", "customDimension10": "", "customDimension11": "66 - The National Archives", "customDimension12": "Level 7 - Item", "customDimension13": "WO 95 - War Office: First World War and Army of Occupation War Diaries", "customDimension14": "WO 95/1510/4 - Headquarters Branches and Services: General Staff.", "customDimension15": "CAT", "customDimension16": "", "customDimension17": "No availability condition provisioned for this record"}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)


class RecordDetailBackToSearchTest(TestCase):
    def setUp(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(record=create_record(iaid="C13359805")),
        )

        self.record_detail_url = reverse(
            "details-page-machine-readable", kwargs={"id": "C13359805"}
        )

        self.expected_button_link_gen_value_fmt = '<a class="cta-primary-panel__link" href="{back_to_search_url}" data-link-type="Link" data-link="Back to search results" data-component-name="Navigation">'
        self.back_to_search_url_timestamp = timezone.now()

    @responses.activate
    def test_back_to_search_render_with_catalogue_search_within_expiry(self):
        """navigation to record details from previous search (session is set since its coming from search catalogue)"""

        search_url_gen_html_resp = "%2Fsearch%2Fcatalogue%2F%3Fsort_by%3Dtitle%26q%3Dlondon%26filter_keyword%3Dpaper%26level%3DItem%26collection%3DADM%26collection%3DBT%26closure%3DOpen%2BDocument%252C%2BOpen%2BDescription%26opening_start_date_0%3D%26opening_start_date_1%3D%26opening_start_date_2%3D1900%26opening_end_date_0%3D%26opening_end_date_1%3D%26opening_end_date_2%3D2020%26per_page%3D20%26display%3Dlist%26page%3D2%26group%3Dtna"

        session = self.client.session
        session["back_to_search_url"] = search_url_gen_html_resp
        session["back_to_search_url_timestamp"] = (
            self.back_to_search_url_timestamp.isoformat()
        )
        session.save()

        response = self.client.get(self.record_detail_url)

        expected_button_link_gen_value = self.expected_button_link_gen_value_fmt.format(
            back_to_search_url=search_url_gen_html_resp,
        )
        self.assertContains(response, expected_button_link_gen_value)

    @responses.activate
    def test_back_to_search_render_with_catalogue_search_beyond_expiry(self):
        """navigation to record details from previous search (session is set since its coming from search catalogue)"""

        search_url_gen_html_resp = "/search/catalogue/"

        session = self.client.session
        session["back_to_search_url"] = search_url_gen_html_resp
        # set time behind the setup value for expiry
        session["back_to_search_url_timestamp"] = (
            self.back_to_search_url_timestamp - SEARCH_URL_RETAIN_DELTA
        ).isoformat()
        session.save()

        response = self.client.get(self.record_detail_url)

        expected_button_link_gen_value = self.expected_button_link_gen_value_fmt.format(
            back_to_search_url=search_url_gen_html_resp,
        )
        self.assertContains(response, expected_button_link_gen_value)

    @responses.activate
    def test_new_search_render_without_session(self):
        """Test covers navigation to record details without a previous search (session is not set since its not coming from search)"""

        new_search_url = reverse("search-catalogue")

        response = self.client.get(self.record_detail_url)

        expected_button_link_gen_value = self.expected_button_link_gen_value_fmt.format(
            back_to_search_url=new_search_url
        )
        self.assertContains(response, expected_button_link_gen_value)

    @responses.activate
    def test_new_search_render_with_session(self):
        """navigation to record details from previous search (session is set since its coming from search featuerd, but without query)"""

        browser_search_url = "/search/featured/"

        session = self.client.session
        session["back_to_search_url"] = browser_search_url
        session["back_to_search_url_timestamp"] = (
            self.back_to_search_url_timestamp.isoformat()
        )
        session.save()

        response = self.client.get(self.record_detail_url)

        expected_button_link_gen_value = self.expected_button_link_gen_value_fmt.format(
            back_to_search_url=browser_search_url,
        )
        self.assertContains(response, expected_button_link_gen_value)
