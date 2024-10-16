import json

from copy import deepcopy
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

import responses

from etna.records.api import get_delivery_options_client, get_records_client
from etna.records.delivery_options import (
    AvailabilityCondition,
    Reader,
    construct_delivery_options,
    get_Dept,
    read_delivery_options,
)
from etna.records.models import Record


class DeliveryOptionsApiTest(TestCase):
    def setUp(self):
        self.delivery_options_client = get_delivery_options_client()

    @responses.activate
    def test_delivery_options_api_valid_call_with_iaid(self):
        # Mock the API response
        return_value = [
            {"options": 14, "surrogateLinks": [], "advancedOrderUrlParameters": None}
        ]

        iaid = "A10000"

        # Define the URL to be mocked and the response
        responses.add(
            method=responses.GET,
            url=settings.DELIVERY_OPTIONS_CLIENT_BASE_URL,
            json=return_value,
            status=200,
        )

        response = self.delivery_options_client.fetch(iaid=iaid)

        self.assertEqual(len(responses.calls), 1)

        # Assert the response data
        self.assertEqual(response, return_value)

        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.DELIVERY_OPTIONS_CLIENT_BASE_URL}?iaid={iaid}",
        )

    @responses.activate
    def test_delivery_options_api_valid_call_with_id(self):
        # Mock the API response
        return_value = [
            {"options": 14, "surrogateLinks": [], "advancedOrderUrlParameters": None}
        ]

        id = "ydydgywgd902-jij828-2718732"

        # Define the URL to be mocked and the response
        responses.add(
            method=responses.GET,
            url=settings.DELIVERY_OPTIONS_CLIENT_BASE_URL,
            json=return_value,
            status=200,
        )

        response = self.delivery_options_client.fetch(id=id)

        self.assertEqual(len(responses.calls), 1)

        # Assert the response data
        self.assertEqual(response, return_value)

        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.DELIVERY_OPTIONS_CLIENT_BASE_URL}?id={id}",
        )

    @responses.activate
    def test_delivery_options_api_call_with_invalid_parameter(self):
        # Mock the API response
        return_value = [
            {"options": 14, "surrogateLinks": [], "advancedOrderUrlParameters": None}
        ]

        unknown_parameter = "ydydgywgd902-jij828-2718732"

        # Define the URL to be mocked and the response
        responses.add(
            method=responses.GET,
            url=settings.DELIVERY_OPTIONS_CLIENT_BASE_URL,
            json=return_value,
            status=200,
        )

        with self.assertRaises(TypeError):
            self.delivery_options_client.fetch(unknown_parameter=unknown_parameter)

    @responses.activate
    def test_delivery_options_api_call_with_extended_payload(self):
        # Mock the API response
        return_value = [
            {
                "options": 7,
                "surrogateLinks": [
                    {
                        "xReferenceId": None,
                        "xReferenceCode": None,
                        "xReferenceName": None,
                        "xReferenceType": "DIGITIZED_DISCOVERY",
                        "xReferenceURL": '<a target="_blank" href="https://www.ancestry.co.uk/search/collections/1687/">Ancestry</a>',
                        "xReferenceDescription": None,
                        "xReferenceSortWord": None,
                    }
                ],
                "advancedOrderUrlParameters": None,
            }
        ]
        iaid = "A10000"

        # Define the URL to be mocked and the response
        responses.add(
            method=responses.GET,
            url=settings.DELIVERY_OPTIONS_CLIENT_BASE_URL,
            json=return_value,
            status=200,
        )

        response = self.delivery_options_client.fetch(iaid=iaid)

        self.assertEqual(len(responses.calls), 1)

        # Assert the response data
        self.assertEqual(response, return_value)

        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.DELIVERY_OPTIONS_CLIENT_BASE_URL}?iaid={iaid}",
        )


class DeliveryOptionsHelpersTest(TestCase):
    records_path = (
        f"{settings.BASE_DIR}/etna/records/tests/fixtures/record_level6_nondigital.json"
    )
    # record = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.records_client = get_records_client()
        # cls.do_client = get_delivery_options_client()
        cls.do_dict = read_delivery_options(settings.DELIVERY_OPTIONS_CONFIG)
        with open(cls.records_path, "r") as f:
            cls.record_contents = json.loads(f.read())

    def setUp(self):
        self.record = Record(deepcopy(self.record_contents["hits"]["hits"][0]))

    def check_assertions(
        self,
        delivery_option: dict,
        availability_condition,
        heading=None,
        av_media=None,
        description=[],
        orderbuttons=[],
        expandlink=None,
        supplemental=[],
    ):
        if heading:
            self.assertEqual(delivery_option["heading"], heading)
        if av_media:
            self.assertEqual(delivery_option["av_media"], av_media)
        for i in range(len(orderbuttons)):
            self.assertIn(
                delivery_option["orderbuttons"][i]["href"],
                orderbuttons[i],
                f"AC {availability_condition}: Orderbuttons at index {i} {orderbuttons[i]} does not match: {delivery_option['orderbuttons'][i]['href']}",
            )
        for i in range(len(description)):
            self.assertIn(
                description[i],
                delivery_option["description"],
                f"AC {availability_condition}: Description at index {i} {description[i]} does not match {delivery_option['description']}",
            )
        if expandlink:
            self.assertIn(expandlink, delivery_option["expandlink"])
        for i in range(len(supplemental)):
            self.assertIn(supplemental[i], delivery_option["supplemental"])

    def update_string(self, string, iaid, surrogate):
        string = string.replace(
            "{ReadersTicketUrl}",
            f"{settings.BASE_TNA_URL}/about/visit-us/researching-here/do-i-need-a-readers-ticket/",
        )
        string = string.replace(
            "{KewBookingSystemUrl}",
            f"{settings.BASE_TNA_URL}/book-a-reading-room-visit/",
        )
        string = string.replace(
            "{RecordCopyingUrl}",
            f"{settings.BASE_DISCOVERY_URL}/pagecheck/start/{iaid}/",
        )
        string = string.replace(
            "{OpeningTimesUrl}", f"{settings.BASE_TNA_URL}/about/visit-us/"
        )
        string = string.replace("{OrderUrl}", "(EDEV-113)")  # Temporary - Jira number
        string = string.replace(
            "{ItemNumOfFilesAndSizeInMB}", "(EDEV-107)"
        )  # Temporary - Jira number
        string = string.replace(
            "{DownloadFormat}", "(EDEV-108)"
        )  # Temporary - Jira number
        string = string.replace("{Price}", "(EDEV-109)")  # Temporary - Jira number
        string = string.replace("{BasketUrl}", f"{settings.BASE_DISCOVERY_URL}/basket/")
        string = string.replace(
            "{AdvancedOrdersEmailAddress}",
            "mailto:advanceddocumentorder@nationalarchives.gov.uk",
        )
        st = ""
        if len(surrogate) > 1:
            for s in surrogate[1:]:
                st += "<li>" + s + "</li>"
        string = string.replace("{SubsWebsiteUrls}", st)
        if len(surrogate) > 0:
            string = string.replace("{FirstWebsiteUrlFull}", surrogate[0])
        else:
            string = string.replace("{FirstWebsiteUrlFull}", "")
        string = string.replace(
            "{AdvanceOrderInformationUrl}", f"{settings.BASE_TNA_URL}/about/visit-us/"
        )
        string = string.replace("{DownloadUrl}", "details/download")

        return string

    def test_construct_delivery_options_InvigilationSafeRoom_Offsite(self):
        doptions = [
            {
                "options": AvailabilityCondition.InvigilationSafeRoom,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "requestthis=ADM 352/556&linkback=",
            }
        ]

        with patch("etna.records.delivery_options.get_reader_type") as mocked_reader:
            mocked_reader.return_value = Reader.OFFSITE

            do = construct_delivery_options(doptions, self.record)

            self.check_assertions(
                do,
                availability_condition=doptions[0]["options"],
                heading="This record can only be seen under supervision at The National Archives",
                av_media=[],
                description="Request a quotation for a copy to be digitised or printed and sent to you.",
                orderbuttons=[
                    f"{settings.BASE_DISCOVERY_URL}/pagecheck/start/C2361422/",
                ],
            )

    def test_construct_delivery_options_InvigilationSafeRoom_Staffin(self):
        doptions = [
            {
                "options": AvailabilityCondition.InvigilationSafeRoom,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "requestthis=ADM 352/556&linkback=",
            }
        ]

        with patch("etna.records.delivery_options.get_reader_type") as mocked_reader:
            mocked_reader.return_value = Reader.STAFFIN

            do = construct_delivery_options(doptions, self.record)

            # Jira ticket EDEV-113 is used as a reminder to get this functionality added at a later stage
            self.check_assertions(
                do,
                availability_condition=doptions[0]["options"],
                heading="You can view this record under supervision in our Invigilation Room",
                description="<p>Your order should be ready to view in 60  minutes.</p>",
                orderbuttons=[
                    "(EDEV-113)",
                ],
            )

    def test_construct_delivery_options_CollectionCare_Offsite(self):
        doptions = [
            {
                "options": AvailabilityCondition.CollectionCare,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "requestthis=ADM 352/556&linkback=",
            }
        ]

        with patch("etna.records.delivery_options.get_reader_type") as mocked_reader:
            mocked_reader.return_value = Reader.OFFSITE

            do = construct_delivery_options(doptions, self.record)

            self.check_assertions(
                do,
                availability_condition=doptions[0]["options"],
                heading="This record requires supervised handling in Collection Care",
                description=f'<p>Please <a href="mailto:{settings.ADVANCED_DOCUMENT_ORDER_EMAIL}"  title="Contact us">contact </a>',
                orderbuttons=[
                    f"mailto:{settings.ADVANCED_DOCUMENT_ORDER_EMAIL}",
                ],
            )

    def test_construct_delivery_options_InUse_Subscription(self):
        doptions = [
            {
                "options": AvailabilityCondition.InUse,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "requestthis=ADM 352/556&linkback=",
            }
        ]

        with patch("etna.records.delivery_options.get_reader_type") as mocked_reader:
            mocked_reader.return_value = Reader.SUBSCRIPTION

            do = construct_delivery_options(doptions, self.record)

            self.check_assertions(
                do,
                availability_condition=doptions[0]["options"],
                heading="Ordering and viewing options",
                description=f'You will need a <a href="{settings.BASE_TNA_URL}/about/visit-us/researching-here/do-i-need-a-readers-ticket/">reader\'s ticket</a> to do this.',
                orderbuttons=[
                    f"{settings.BASE_TNA_URL}/book-a-reading-room-visit/",
                    f"{settings.BASE_DISCOVERY_URL}/pagecheck/start/C2361422/",
                ],
            )

    def test_construct_delivery_options_DigitizedLia_Offsite(self):
        doptions = [
            {
                "options": AvailabilityCondition.DigitizedLia,
                "surrogateLinks": [
                    {
                        "xReferenceId": None,
                        "xReferenceCode": None,
                        "xReferenceName": None,
                        "xReferenceType": "DIGITIZED_LIA",
                        "xReferenceURL": '<a target="_blank" href="https://www.ancestry.co.uk/search/collections/7572/">Ancestry</a>',
                        "xReferenceDescription": None,
                        "xReferenceSortWord": None,
                    },
                    {
                        "xReferenceId": None,
                        "xReferenceCode": None,
                        "xReferenceName": None,
                        "xReferenceType": "DIGITIZED_LIA",
                        "xReferenceURL": '<a target="_blank" href="https://www.thegenealogist.co.uk/census/1881/">The Genealogist</a>',
                        "xReferenceDescription": None,
                        "xReferenceSortWord": None,
                    },
                    {
                        "xReferenceId": None,
                        "xReferenceCode": None,
                        "xReferenceName": None,
                        "xReferenceType": "DIGITIZED_LIA",
                        "xReferenceURL": '<a target="_blank" href="https://search.findmypast.co.uk/search-world-Records/1881-england-wales-and-scotland-census">Findmypast</a>',
                        "xReferenceDescription": None,
                        "xReferenceSortWord": None,
                    },
                ],
                "advancedOrderUrlParameters": "requestthis=ADM 352/556&linkback=",
            }
        ]

        with patch("etna.records.delivery_options.get_reader_type") as mocked_reader:
            mocked_reader.return_value = Reader.OFFSITE

            do = construct_delivery_options(doptions, self.record)

            self.check_assertions(
                do,
                availability_condition=doptions[0]["options"],
                heading=f"This is available to download from  {doptions[0]['surrogateLinks'][0]['xReferenceURL']}",
                description="<p>Partner websites are free to search but there may be a charge to view full transcriptions and download documents. Other services may also be available.</p>",
                orderbuttons=[
                    'href="https://www.ancestry.co.uk/search/collections/7572/"'
                ],
                supplemental=f"{doptions[0]['surrogateLinks'][1]['xReferenceURL']}",
            )

    def test_construct_delivery_options_DigitizedLia_Offsite_No_SurrogateLinks(self):
        doptions = [
            {
                "options": AvailabilityCondition.DigitizedLia,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "requestthis=ADM 352/556&linkback=",
            }
        ]

        with patch("etna.records.delivery_options.get_reader_type") as mocked_reader:
            mocked_reader.return_value = Reader.OFFSITE

            do = construct_delivery_options(doptions, self.record)

            self.check_assertions(
                do,
                availability_condition=doptions[0]["options"],
                heading="",
                description="<p>Partner websites are free to search but there may be a charge to view full transcriptions and download documents. Other services may also be available.</p>",
            )

    def test_construct_delivery_options_AV_Media_Offsite(self):
        doptions = [
            {
                "options": AvailabilityCondition.AV_Media,
                "surrogateLinks": [
                    {
                        "xReferenceId": None,
                        "xReferenceCode": None,
                        "xReferenceName": None,
                        "xReferenceType": "AV_MEDIA",
                        "xReferenceURL": '<a target="_blank" href="https://staging-discovery.nationalarchives.gov.uk/VideoPlayer/?url=https://ds-live-videos.s3.amazonaws.com/66/LEV/1/2011-12-13pm">Discovery Video Player</a>',
                        "xReferenceDescription": None,
                        "xReferenceSortWord": None,
                    }
                ],
                "advancedOrderUrlParameters": "requestthis=ADM 352/556&linkback=",
            }
        ]

        with (
            patch("etna.records.delivery_options.get_reader_type") as mocked_reader,
            patch("etna.records.delivery_options.get_dcs_prefixes") as mocked_dcs,
        ):
            mocked_reader.return_value = Reader.OFFSITE
            mocked_dcs.return_value = "IR"

            do = construct_delivery_options(doptions, self.record)

            self.check_assertions(
                do,
                availability_condition=doptions[0]["options"],
                heading=f"View this on the {doptions[0]['surrogateLinks'][0]['xReferenceURL']}",
                description="<p>This document may include content that reflects the trauma and distress experienced by those present during or affected by the tragic events of 15 April  1989.</p>",
                orderbuttons=[
                    f"OB: {doptions[0]['surrogateLinks'][0]['xReferenceURL']}"
                ],
            )

    def test_construct_delivery_options_ClosedRetainedDeptKnown_OnsitePublic_Valid_Prefix(
        self,
    ):
        doptions = [
            {
                "options": AvailabilityCondition.ClosedRetainedDeptKnown,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": None,
            }
        ]

        with (
            patch("etna.records.delivery_options.get_reader_type") as mocked_reader,
            patch("etna.records.delivery_options.get_dcs_prefixes") as mocked_dcs,
        ):
            mocked_reader.return_value = Reader.ONSITEPUBLIC
            mocked_dcs.return_value = "XYZ"

            self.record.reference_number = "FCO 123/3"
            self.record.access_condition = "Currently unavailable"

            do = construct_delivery_options(doptions, self.record)

            self.check_assertions(
                do,
                availability_condition=doptions[0]["options"],
                heading='This record is closed and retained by the <a href="http://www.fco.gov.uk/en/publications-and-documents/freedom-of-information/" target="_blank">Foreign and Commonwealth Office</a>',
                description=f"<p>  <strong>{self.record.access_condition}</strong><br />",
                orderbuttons=[
                    "http://www.fco.gov.uk/en/publications-and-documents/freedom-of-information/"
                ],
            )

    def test_construct_delivery_options_ClosedRetainedDeptKnown_OnsitePublic_Invalid_Prefix(
        self,
    ):
        # If a 'closed retained deprtment known' record does not have a prefix specific to a government website, it needs
        # to be changed to 'closed retained department unknown'

        doptions = [
            {
                "options": AvailabilityCondition.ClosedRetainedDeptKnown,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": None,
            }
        ]

        with patch("etna.records.delivery_options.get_reader_type") as mocked_reader:
            mocked_reader.return_value = Reader.ONSITEPUBLIC

            self.record.reference_number = "BT 123/3"

            do = construct_delivery_options(doptions, self.record)

            self.check_assertions(
                do,
                availability_condition=doptions[0]["options"],
                heading="This record is retained by a government department",
            )

    def test_construct_delivery_options_Invalid_DO_Exception(self):
        doptions = [
            {
                "options": AvailabilityCondition.OrderException,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": None,
            }
        ]

        with patch("etna.records.delivery_options.get_reader_type") as mocked_reader:
            mocked_reader.return_value = Reader.ONSITEPUBLIC

            self.record.reference_number = "BT 123/3"

            do = construct_delivery_options(doptions, self.record)

            self.check_assertions(
                do,
                availability_condition=doptions[0]["options"],
                heading="Order and viewing options error",
                description="This service is currently unavailable.  We apologise for any inconvenience caused.",
            )

    def test_get_dept(self):
        self.assertEqual(get_Dept("DEFE 12/3", "deptname"), "Ministry of Defence")
        self.assertEqual(
            get_Dept("DEFE 12/3", "depturl"),
            "https://www.gov.uk/government/organisations/ministry-of-defence",
        )

        self.assertEqual(get_Dept("T 352/2/3", "deptname"), "Cabinet Office")
        self.assertEqual(
            get_Dept("T 352/2/3", "depturl"),
            "http://www.cabinetoffice.gov.uk/content/freedom-information-foi",
        )

        self.assertIsNone(get_Dept("XYZ 12/3", "deptname"))
