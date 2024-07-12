from enum import IntEnum
import json
import re
from django.conf import settings
from typing import Any, Dict, List, Union, Tuple

class Reader(IntEnum):
    STAFFIN = 0
    ONSITEPUBLIC = 1
    SUBSCRIPTION = 2
    OFFSITE = 3


class AvailabiltyCondition(IntEnum):
    InvigilationSafeRoom = 0
    CollectionCare = 1
    InUse = 2
    DigitizedDiscovery = 3
    DigitizedLia = 4
    DigitizedOther = 5
    DigitizedAvailableButNotDownloadableAtPieceLevel = 6
    DigitizedAvailableButNotDownloadableAtItemLevel = 7
    DigitizedPartiallyOpened = 8
    AV_Media = 9
    AcademicSubscription = 10
    ImageLibrary = 11
    ClosedFOIReview = 12
    AccessUnderReview = 13
    ClosedRetainedDeptKnown = 14
    ClosedRetainedDeptUnKnown = 15
    PaidSearch = 16
    Offsite = 17
    Surrogate = 18
    Unfit = 19
    MouldTreatment = 20
    Onloan = 21
    DisplayAtMuseum = 22
    MissingLost = 23
    GovtWebArchive = 24
    LocalArchive = 25
    OrderOriginal = 26
    FileAuthority = 27
    TooLargeToCopyOriginal = 28
    TooLargeToCopyOffsite = 29
    TooLargeToCopySurrogate = 30
    UnAvailable = 31
    OrderException = 32
    AdvanceOrderOnly = 33
    Relocation = 34


dept_details = {
    "AB": {
        "deptname": "Nuclear Decommissioning Authority",
        "depturl": "https://www.gov.uk/government/organisations/nuclear-decommissioning-authority",
    },
    "ADM": {
        "deptname": "Ministry of Defence",
        "depturl": "https://www.gov.uk/government/organisations/ministry-of-defence",
    },
    "AIR": {
        "deptname": "Ministry of Defence",
        "depturl": "https://www.gov.uk/government/organisations/ministry-of-defence",
    },
    "CAB": {
        "deptname": "Cabinet Office",
        "depturl": "http://www.cabinetoffice.gov.uk/content/freedom-information-foi",
    },
    "CO": {
        "deptname": "Foreign and Commonwealth Office",
        "depturl": "http://www.fco.gov.uk/en/publications-and-documents/freedom-of-information/",
    },
    "COAL": {
        "deptname": "Department for Business, Energy and Industrial Strategy",
        "depturl": "https://www.gov.uk/government/organisations/department-for-business-energy-and-industrial-strategy",
    },
    "DEFE": {
        "deptname": "Ministry of Defence",
        "depturl": "https://www.gov.uk/government/organisations/ministry-of-defence",
    },
    "DO": {
        "deptname": "Foreign and Commonwealth Office",
        "depturl": "http://www.fco.gov.uk/en/publications-and-documents/freedom-of-information/",
    },
    "ES": {
        "deptname": "Ministry of Defence",
        "depturl": "https://www.gov.uk/government/organisations/ministry-of-defence",
    },
    "FCO": {
        "deptname": "Foreign and Commonwealth Office",
        "depturl": "http://www.fco.gov.uk/en/publications-and-documents/freedom-of-information/",
    },
    "FO": {
        "deptname": "Foreign and Commonwealth Office",
        "depturl": "http://www.fco.gov.uk/en/publications-and-documents/freedom-of-information/",
    },
    "PREM": {
        "deptname": "Cabinet Office",
        "depturl": "http://www.cabinetoffice.gov.uk/content/freedom-information-foi",
    },
    "T 352": {
        "deptname": "Cabinet Office",
        "depturl": "http://www.cabinetoffice.gov.uk/content/freedom-information-foi",
    },
    "WO": {
        "deptname": "Ministry of Defence",
        "depturl": "https://www.gov.uk/government/organisations/ministry-of-defence",
    },
    # Add more departments as needed
}


def get_Dept(reference_number: str, field: str):
    """
    The reference_number is the entire reference, e.g. "PROB 11/1022/1" or "RAIL 1005/190"
    We are looking to see if the first x characters of the reference_number match the key in
    the dept_details dictionary above.

    The key is either 'deptname' or 'depturl'
    """

    for key, value in dept_details.items():
        if reference_number.startswith(key):
            return value[field]
        
    if field == 'deptname':
        return "a government department"
    else:
        return " "


"""
    Helper functions that provide the logic to return values for {xyz} tags in the DeliveryOptions.json file. 
    Some are simple urls or text strings, others require data from elsewhere in order to calculate them.
"""

def get_AccessConditionText(record: dict, surrogate: List) -> str:
    if ac := record.access_condition:  # If it's not None, return it
        return ac
    return " "

def get_AddedToBasketText(record: dict, surrogate: List) -> str:
    return "Add to basket"

def get_AdvancedOrdersEmailAddress(record: dict, surrogate: List) -> str:
    return "mailto:advanceddocumentorder@nationalarchives.gov.uk"

def get_AdvanceOrderInformationUrl(record: dict, surrogate: List) -> str:
    return f"{settings.BASE_TNA_URL}/about/visit-us/"

def get_ArchiveLink(record: dict, surrogate: List) -> str:
    return record.held_by_url

def get_ArchiveName(record: dict, surrogate: List) -> str:
    return record.held_by

def get_BasketType(record: dict, surrogate: List) -> str:  # Unknown derivation
    return "(EDEV-113)"

def get_BasketUrl(record: dict, surrogate: List) -> str:
    return f"{settings.BASE_DISCOVERY_URL}/basket/"

def get_BrowseUrl(record: dict, surrogate: List) -> str:  # Unknown derivation
    return "(EDEV-112)"

def get_ContactFormUrl(record: dict, surrogate: List) -> str:
    return f"{settings.BASE_TNA_URL}/contact-us/"

def get_DataProtectionActUrl(record: dict, surrogate: List) -> str:
    return f"{settings.BASE_DISCOVERY_URL}/Content/documents/county-durham-home-guard-service-record-subject-access-request-form.pdf"

def get_DeptName(record: dict, surrogate: List) -> str:
    if name := get_Dept(record.reference_number, "deptname"):
        return name
    else:
        return ""
    
def get_DeptUrl(record: dict, surrogate: List) -> str:
    if url := get_Dept(record.reference_number, "depturl"):
        return url
    else:
        return ""

def get_DownloadFormat(record: dict, surrogate: List) -> str:
    return "(EDEV-108)"

def get_DownloadText(record: dict, surrogate: List) -> str:
    return "Download now"

def get_DownloadUrl(record: dict, surrogate: List) -> str:
    return f"details/download"

def get_FAType(record: dict, surrogate: List) -> str:  # Unknown derivation
    return "(EDEV-111)"

def get_FoiUrl(record: dict, surrogate: List) -> str:
    return (
        f"{settings.BASE_DISCOVERY_URL}/foirequest?reference={record.reference_number}"
    )

def get_ImageLibraryUrl(record: dict, surrogate: List) -> str:
    return "https://images.nationalarchives.gov.uk/"

def get_ItemNumOfFilesAndSizeInMB(record: dict, surrogate: List) -> str:
    return "(EDEV-107)"

def get_KeepersGalleryUrl(record: dict, surrogate: List) -> str:
    return f"{settings.BASE_TNA_URL}/about/visit-us/whats-on/keepers-gallery/"

def get_KewBookingSystemUrl(record: dict, surrogate: List) -> str:
    return f"{settings.BASE_TNA_URL}/book-a-reading-room-visit/"

def get_MaxItems(record: dict, surrogate: List) -> str:
    return settings.MAX_BASKET_ITEMS

def get_OpenDateDesc(record: dict, surrogate: List) -> str:
    if record.record_opening:
        return "Opening date: "
    return " "

def get_OpeningTimesUrl(record: dict, surrogate: List) -> str:
    return f"{settings.BASE_TNA_URL}/about/visit-us/"

def get_OrderUrl(record: dict, surrogate: List) -> str:
    return "(EDEV-113)"

def get_PaidSearchUrl(record: dict, surrogate: List) -> str:
    return f"{settings.BASE_DISCOVERY_URL}/paidsearch/foirequest/{record.iaid}"

def get_Price(record: dict, surrogate: List) -> str:
    return "(EDEV-109)"

def get_ReadersTicketUrl(record: dict, surrogate: List) -> str:
    return f"{settings.BASE_TNA_URL}/about/visit-us/researching-here/do-i-need-a-readers-ticket/"

def get_RecordCopyingUrl(record: dict, surrogate: List) -> str:
    return f"{settings.BASE_DISCOVERY_URL}/pagecheck/start/{record.iaid}/"

def get_RecordInformationType(record: dict, surrogate: List) -> str:
    return "(EDEV-110)"

def get_RecordOpeningDate(record: dict, surrogate: List) -> str:
    if rod := record.record_opening:
        return rod
    return " "

def get_RecordUrl(record: dict, surrogate: List) -> str:
    return f"{settings.BASE_DISCOVERY_URL}/details/r/{record.parent.iaid}/"

def get_FirstWebsiteUrl(record: dict, surrogate: List) -> str:
    # This comes from the delivery options surrogate dictionary. They all have html markup
    # embedded in them but this particular case is for a button, so we need to extract the 
    # href from the string.
    if len(surrogate) > 0:
        match = re.search(r'href="([^"]+)"', surrogate[0])

        return match.group(1) if match else ""
    else:
        return ""

def get_FirstWebsiteUrlFull(record: dict, surrogate: List) -> str:
    if len(surrogate) > 0:
        return surrogate[0]
    else:
        return ""

def get_SubsequentWebsiteUrls(record: dict, surrogate: List) -> str:
    st = " "
    if len(surrogate) > 1:
        for s in surrogate[1:]:
            st += "<li>" + s + "</li>"
    return st

def get_AllWebsiteUrls(record: dict, surrogate: List) -> str:
    st = " "
    for s in surrogate:
        st += "<li>" + s + "</li>"
    return st

# Temporary
def get_WebsiteUrls(record: dict, surrogate: List) -> str:
    st = " "
    for s in surrogate[1:]:
        st += "<li>" + s + "</li>"
    return st

# Temporary
def get_WebsiteUrl(record: dict, surrogate: List) -> str:
    return surrogate[0]

def get_WebsiteUrlText(record: dict, surrogate: List) -> str:
    pattern = r">(.*?)<"

    if len(surrogate):
        match = re.search(pattern, surrogate[0])
        return match.group(1) if match else ""
    else:
        return " "

def get_YourOrderLink(record: dict, surrogate: List) -> str:
    return "(EDEV-113)"


# This dict links the embedded tags with a helper function that returns the
# correct inserted value, e.g. url's
deliveryOptionsTags = {
    "{AccessConditionText}": get_AccessConditionText,
    "{AddedToBasketText}": get_AddedToBasketText,
    "{AdvancedOrdersEmailAddress}": get_AdvancedOrdersEmailAddress,
    "{AdvanceOrderInformationUrl}": get_AdvanceOrderInformationUrl,
    "{ArchiveLink}": get_ArchiveLink,
    "{ArchiveName}": get_ArchiveName,
    "{BasketType}": get_BasketType,
    "{BasketUrl}": get_BasketUrl,
    "{BrowseUrl}": get_BrowseUrl,
    "{ContactFormUrl}": get_ContactFormUrl,
    "{DataProtectionActUrl}": get_DataProtectionActUrl,
    "{DeptName}": get_DeptName,
    "{DeptUrl}": get_DeptUrl,
    "{DownloadFormat}": get_DownloadFormat,
    "{DownloadText}": get_DownloadText,
    "{DownloadUrl}": get_DownloadUrl,
    "{FAType}": get_FAType,
    "{FoiUrl}": get_FoiUrl,
    "{ImageLibraryUrl}": get_ImageLibraryUrl,
    "{ItemNumOfFilesAndSizeInMB}": get_ItemNumOfFilesAndSizeInMB,
    "{KeepersGalleryUrl}": get_KeepersGalleryUrl,
    "{KewBookingSystemUrl}": get_KewBookingSystemUrl,
    "{MaxItems}": get_MaxItems,
    "{OpenDateDesc}": get_OpenDateDesc,
    "{OpeningTimesUrl}": get_OpeningTimesUrl,
    "{OrderUrl}": get_OrderUrl,
    "{PaidSearchUrl}": get_PaidSearchUrl,
    "{Price}": get_Price,
    "{ReadersTicketUrl}": get_ReadersTicketUrl,
    "{RecordCopyingUrl}": get_RecordCopyingUrl,
    "{RecordInformationType}": get_RecordInformationType,
    "{RecordOpeningDate}": get_RecordOpeningDate,
    "{RecordUrl}": get_RecordUrl,
    "{AllWebsiteUrls}": get_AllWebsiteUrls,
    "{SubsWebsiteUrls}": get_SubsequentWebsiteUrls,
    "{FirstWebsiteUrl}": get_FirstWebsiteUrl,
    "{FirstWebsiteUrlFull}": get_FirstWebsiteUrlFull,
    "{WebsiteUrlText}": get_WebsiteUrlText,
    "{YourOrderLink}": get_YourOrderLink,
}

# Dictionary to serve as a cache for file contents, preventing redundant file reads
file_cache = {}


def read_delivery_options(file_path: str) -> List:
    # Check if file content is already in the cache
    if file_path not in file_cache:
        # Open the file in read mode
        with open(file_path, "r") as file:
            # Load the JSON content from the file
            file_content = json.load(file)

            # Cache the file content for future use
            file_cache[file_path] = file_content

    # Return the file content either from the cache or newly loaded
    return file_cache[file_path]

def get_dcs_prefixes() -> List:
    dcs = settings.DELIVERY_OPTIONS_DCS_LIST
    return dcs.split()

def distressing_content_match(reference: str) -> bool:
    dcs_prefixes = get_dcs_prefixes()

    return list(filter(reference.startswith, dcs_prefixes)) != []


def get_record(cache: Dict, record_id: int):
    try:
        return cache["deliveryOptions"]["option"][record_id]
    except:
        return None


def html_replacer(string: str, record: dict, surrogate_data: List) -> str:
    subs = re.findall(r"{[A-Za-z]*}", string)

    for s in subs:
        try:
            func = deliveryOptionsTags[s]

            # If the tag doesn't have any data (can happen with surrogate links),
            # rather than have a string with something missing, just return an
            # empty string and it won't get displayed
            if f := func(record, surrogate_data):
                string = string.replace(s, f)
        except:
            raise
    return string


def html_builder(
    delivery_option_data: Union[List, str],
    record_data: Dict,
    surrogate_data: List = [],
    dcs: bool = False,
) -> str:
    html = ""

    if delivery_option_data is None:
        return html

    if isinstance(delivery_option_data, list):
        for item in delivery_option_data:
            if not dcs and item["name"] == "descriptionDCS":
                pass
            else:
                html += html_replacer(item["value"], record_data, surrogate_data)
    else:
        html = html_replacer(delivery_option_data, record_data, surrogate_data)

    return html


# Specific pre-processing for the order buttons data
def orderbuttons_builder(
    delivery_option_data: List, record_data: Dict, surrogate_data: List
) -> List:
    for item in delivery_option_data:
        item["href"] = html_builder(
            item["href"], record_data, surrogate_data=surrogate_data
        )
        item["text"] = html_builder(
            item["text"], record_data, surrogate_data=surrogate_data
        )
    return delivery_option_data


# Specific pre-processing for the basket limit data
def basketlimit_builder(
    delivery_option_data: Union[List, str], record_data: Dict
) -> str:
    return html_builder(delivery_option_data, record_data)


# Specific pre-processing for the expand link data
def expandlink_builder(
    delivery_option_data: Union[List, str], record_data: Dict
) -> str:
    return html_builder(delivery_option_data, record_data)


# Specific pre-processing for the description data
def description_builder(
    delivery_option_data: Union[List, str], record_data: Dict, surrogate_data: List
) -> str:
    if distressing_content_match(record_data.reference_number):
        return html_builder(
            delivery_option_data, record_data, surrogate_data=surrogate_data, dcs=True
        )
    
    return html_builder(
        delivery_option_data, record_data, surrogate_data=surrogate_data
    )


# Specific pre-processing for the supplemental data
def supplemental_builder(
    delivery_option_data: Union[List, str], record_data: Dict, surrogate_data: List
) -> str:
    return html_builder(
        delivery_option_data, record_data, surrogate_data=surrogate_data
    )


# Specific pre-processing for the heading
def heading_builder(
    delivery_option_data: str, record_data: Dict, surrogate_data: List
) -> str:
    return html_builder(
        delivery_option_data, record_data, surrogate_data=surrogate_data
    )


def surrogate_link_builder(surrogates: List) -> Tuple[List[Any], List[Any]]:
    surrogate_list = []
    av_media_list = []

    for s in surrogates:
        surrogate_list.append(s["xReferenceURL"])

        if s["xReferenceType"] == "AV_MEDIA":
            av_media_list.append(s["xReferenceURL"])

    return surrogate_list, av_media_list

""" The following four functions are used to determine the reader type. These are
to be written under ticket EDEV-115 when enough is known about the mechanism """

def is_onsite() -> bool:
    return False

def is_subscribed() -> bool:
    return False

def is_staff() -> bool:
    return False

def get_reader_type() -> Reader:
    # EDEV-115
    # Code to determine status of reader (see enum Reader above).
    reader = Reader.OFFSITE

    if is_subscribed():
        reader = Reader.SUBSCRIPTION
    elif is_onsite():
        reader = Reader.ONSITEPUBLIC
    elif is_staff():
        reader = Reader.STAFFIN

    return reader

""" End of EDEV-115 """

# Main routine called from records.py
def construct_delivery_options(doptions: list, record: dict) -> dict:
    do = {}

    # EDEV-115
    reader_type = get_reader_type()
    
    do_dict = read_delivery_options(settings.DELIVERY_OPTIONS_CONFIG)

    # To do: The doptions list contains zero or more dictionaries. Only 1 should be
    # allowed, so fail on zero or greater than 1

    # Surrogate links is always present as a list, which can be empty
    do["surrogate"], do["av_media"] = surrogate_link_builder(
        doptions[0]["surrogateLinks"]
    )

    # if surrogate links is not an empty list, it will contain one or more dictionaries of the form:
    """     {
                "xReferenceId": null,
                "xReferenceCode": null,
                "xReferenceName": null,
                "xReferenceType": "DIGITIZED_DISCOVERY",
                "xReferenceURL": "<a target=\"_blank\" href=\"https://www.thegenealogist.co.uk/non-conformist-records\">The Genealogist</a>",
                "xReferenceDescription": null,
                "xReferenceSortWord": null
            },
    """

    # Get the specific delivery option for this artefact
    delivery_option = get_record(do_dict, doptions[0]["options"])

    reader_option = delivery_option["readertype"][reader_type]

    # The reader_option has the following fields:
    #   reader - (staffin/onsitepublic/subsription/offsite) - mandatory
    #   description - is a list of one or more dictionaries containing name and value fields - optional
    #       NOTE: there is a special case when the description name is 'descriptionDCS' - this is for distressing material
    #   heading - string - optional.
    #   orderbuttons - a string containing html for buttons in an unordered list - optional
    #   supplementalcontent - is a list of one or more dictionaries containing name and value fields - optional

    if title := reader_option.get("heading"):
        do["heading"] = heading_builder(title, record, do["surrogate"])

    if text := reader_option.get("description"):
        do["description"] = description_builder(text, record, do["surrogate"])

    if supp := reader_option.get("supplementalcontent"):
        do["supplemental"] = supplemental_builder(supp, record, do["surrogate"])

    if obutton := reader_option.get("orderbuttons"):
        do["orderbuttons"] = orderbuttons_builder(obutton, record, do["surrogate"])

    if expand := reader_option.get("expandlink"):
        do["expandlink"] = expandlink_builder(expand, record)

    if basket := reader_option.get("basketlimit"):
        do["basketlimit"] = basketlimit_builder(basket, record)

    #do['debug1'] = do

    return do
