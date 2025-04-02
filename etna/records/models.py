from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Union

from django.conf import settings
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from pyquery import PyQuery as pq

from etna.analytics.mixins import DataLayerMixin
from etna.ciim.constants import (
    ARCHIVE_NRA_RECORDS_COLLECTION,
    ARCHIVE_RECORD_CREATORS_COLLECTION,
    TNA_URLS,
)
from etna.ciim.models import APIModel
from etna.ciim.utils import (
    NOT_PROVIDED,
    ValueExtractionError,
    extract,
    find,
    find_all,
    format_link,
    strip_html,
)
from etna.records.classes import (
    AccessionsInfo,
    ArchiveCollections,
    CollectionInfo,
    ContactInfo,
    FurtherInfo,
)

from .converters import IAIDConverter

logger = logging.getLogger(__name__)


class Record(DataLayerMixin, APIModel):
    """A 'lazy' data-interaction layer for record data retrieved from the Client API"""

    def __init__(self, raw_data: Dict[str, Any]):
        """
        This method recieves the raw JSON data dict recieved from
        Client API and makes it available to the instance as `self._raw`.
        """
        self._raw = raw_data.get("_source") or raw_data
        self.score = raw_data.get("_score")
        self.highlights = raw_data.get("highlight") or {}

    @classmethod
    def from_api_response(cls, response: dict) -> Record:
        return cls(response)

    def __str__(self):
        return f"{self.summary_title} ({self.iaid})"

    def get(self, key: str, default: Optional[Any] = NOT_PROVIDED):
        """
        Attempts to extract `key` from `self._raw` and return the value.

        Raises `ciim.utils.ValueExtractionError` if the value cannot be extracted.
        """
        if "." in key:
            return extract(self._raw, key, default)
        try:
            return self._raw[key]
        except KeyError as e:
            if default is NOT_PROVIDED:
                raise ValueExtractionError(str(e))
            return default

    @cached_property
    def template(self) -> Dict[str, Any]:
        return self.get("@template.details", default=self.get("@template.results", {}))

    @cached_property
    def iaid(self) -> str:
        """
        Return the "iaid" value for this record. If the data is unavailable,
        or is not a valid iaid, a blank string is returned.
        """
        try:
            candidate = self.template["iaid"]
        except KeyError:
            candidate = self.get("@admin.id", default="")

        try:
            # fallback for Record Creators
            if not candidate:
                candidate = self.template["primaryIdentifier"]
        except KeyError:
            candidate = ""

        if candidate and re.match(IAIDConverter.regex, candidate):
            # value is not guaranteed to be a valid 'iaid', so we must
            # check it before returning it as one
            return candidate
        return ""

    @property
    def pk(self):
        return self.iaid

    @cached_property
    def reference_number(self) -> str:
        """
        Return the "reference_number" value for this record, or a blank
        string if no such value can be found in the usual places.
        """
        try:
            return self.template["referenceNumber"]
        except KeyError:
            pass
        identifiers = self.get("identifier", ())
        for item in identifiers:
            try:
                return item["reference_number"]
            except KeyError:
                pass
        return ""

    def reference_prefixed_summary_title(self):
        return f"{self.reference_number or 'N/A'} - {self.summary_title}"

    @cached_property
    def source_url(self):
        """
        Return the "url" value for this record. This value is typically
        only present for 'interpretive' results from other websites.

        Raises `ValueExtractionError` when the raw data does not include
        values in any of the expected positions.
        """
        try:
            return self.template["sourceUrl"]
        except KeyError:
            raise ValueExtractionError(
                f"'source_url' could not be extracted from source data: {self._raw}"
            )

    def has_source_url(self) -> bool:
        """
        Returns `True` if a 'source_url' value can be extracted from the raw data
        for this record. Otherwise `False`.
        """
        try:
            self.source_url
        except ValueExtractionError:
            return False
        else:
            return True

    @cached_property
    def summary_title(self) -> str:
        if raw := self._get_raw_summary_title():
            return mark_safe(strip_html(raw, preserve_marks=True, ensure_spaces=True))
        return raw

    def _get_raw_summary_title(self) -> str:
        try:
            return "... ".join(self.highlights["@template.details.summaryTitle"])
        except KeyError:
            pass
        try:
            return self.template["summaryTitle"]
        except KeyError:
            pass
        return self.get("summary.title", default="")

    def get_url(self, use_reference_number: bool = True) -> str:
        if use_reference_number and self.reference_number:
            try:
                return reverse(
                    "details-page-human-readable",
                    kwargs={"reference_number": self.reference_number},
                )
            except NoReverseMatch:
                pass
        if self.iaid:
            try:
                return reverse(
                    "details-page-machine-readable", kwargs={"iaid": self.iaid}
                )
            except NoReverseMatch:
                pass

        if self.has_source_url():
            return self.source_url
        return ""

    @cached_property
    def url(self) -> str:
        return self.get_url()

    @cached_property
    def non_reference_number_url(self) -> str:
        return self.get_url(use_reference_number=False)

    @cached_property
    def is_tna(self):
        for item in self.get("@datatype.group", ()):
            if item.get("value", "") == "tna":
                return True
        return False

    @cached_property
    def type(self) -> Union[str, None]:
        try:
            return self.template["type"]
        except KeyError:
            return self.get("@datatype.base", None)

    @cached_property
    def access_condition(self) -> str:
        try:
            return self.template["accessCondition"]
        except KeyError:
            self.get("availability.access.condition.value", default="")
        return

    @cached_property
    def arrangement(self) -> str:
        try:
            raw = self.template["arrangement"]
        except KeyError:
            raw = self.get("arrangement.value", default="")
        return mark_safe(raw)

    @cached_property
    def legal_status(self) -> str:
        try:
            return self.template["legalStatus"]
        except KeyError:
            return self.get("legal.status", default="")

    @cached_property
    def is_digitised(self) -> bool:
        return self.get("digitised", default=self.template.get("digitised", False))

    @cached_property
    def availability_delivery_surrogates(self) -> str:
        return self.get("availability.delivery.surrogate", default="")

    @cached_property
    def media_reference_id(self) -> str:
        return self.get("multimedia.@admin.id", default="")

    @cached_property
    def source(self) -> str:
        return self.get("source.value", default="")

    @cached_property
    def description(self) -> str:
        """
        Returns the records full description value with all HTML left intact.
        """
        return mark_safe(self._get_raw_description())

    @cached_property
    def listing_description(self) -> str:
        """
        Returns a version of the record's description that is safe to use
        anywhere. When highlight data is provided by the API, <mark> tags
        will be left in-tact, but and other HTML is stripped.
        """
        if raw := self._get_raw_description(use_highlights=True):
            return mark_safe(strip_html(raw, preserve_marks=True, ensure_spaces=True))
        return ""

    def _get_raw_description(self, use_highlights: bool = False) -> str:
        if use_highlights:
            try:
                return "... ".join(self.highlights["@template.details.description"])
            except KeyError:
                pass
        try:
            return self.template["description"]
        except KeyError:
            pass
        description_items = self.get("description", ())
        for item in description_items:
            if item.get("type", "") == "description" or len(description_items) == 1:
                return item.get("value", "")
        return ""

    @cached_property
    def content(self) -> str:
        if raw := self._get_raw_content():
            return strip_html(raw)
        return ""

    def _get_raw_content(self) -> str:
        for item in self.get("source.content", ()):
            return item
        return ""

    @cached_property
    def held_by(self) -> str:
        return self.template.get("heldBy", "")

    @cached_property
    def held_by_id(self) -> str:
        return self.template.get("heldById", "")

    @cached_property
    def held_by_url(self) -> str:
        if self.held_by_id:
            try:
                return reverse(
                    "details-page-machine-readable",
                    kwargs={"iaid": self.held_by_id},
                )
            except NoReverseMatch:
                pass
        return ""

    @cached_property
    def date_created(self) -> str:
        return self.template.get("dateCreated", "")

    @cached_property
    def record_opening(self) -> str:
        return self.template.get("recordOpening", "")

    @cached_property
    def level(self) -> str:
        return self.get("level.value", self.template.get("level", ""))

    @cached_property
    def level_code(self) -> int:
        return self.get("level.code", None)

    @cached_property
    def delivery_option(self) -> str:
        return self.template.get("deliveryOption", "")

    @property
    def availability_condition_category(self) -> str:
        return settings.AVAILABILITY_CONDITION_CATEGORIES.get(self.delivery_option, "")

    @cached_property
    def repo_summary_title(self) -> str:
        return self.get("repository.summary.title", default="")

    @cached_property
    def repository(self) -> Union["Record", None]:
        if repository := self.get("repository", default=None):
            return Record(repository)

    @cached_property
    def repo_archon_value(self) -> str:
        for item in self.get("repository.identifier", ()):
            if item["type"] == "Archon number":
                return item.get("value", "")
        return ""

    @cached_property
    def parent(self) -> Union["Record", None]:
        if parent_data := self.get("parent.0", default=None):
            return Record(parent_data)

    @cached_property
    def hierarchy(self) -> Tuple["Record"]:
        # TODO Leaving this here for potential later use for testing the data for the front-end aspects.
        # This is to create spoof data for the missing API data from K-int. Can be removed from code when

        # for item in self.get("@hierarchy.0", default=()):
        #     if not item.get("identifier"):
        #         level = item.get("level", {})
        #         level_code = level.get("code", "")
        #         hierarchy = self.get("@hierarchy.0", ())
        #         if hierarchy != () and level_code != "":
        #             previous_level_record = hierarchy[level_code-2]
        #             previous_level_identifier = previous_level_record.get("identifier")[0]
        #             previous_level_reference = previous_level_identifier.get("reference_number")
        #             if level_code == 2:
        #                 reference_number = "Division within " + previous_level_reference
        #             elif level_code == 4:
        #                 reference_number = "Sub-series within " + previous_level_reference
        #             item["identifier"] = [{'primary': True, 'reference_number': reference_number, 'type': 'reference number', 'value': reference_number}]
        return tuple(
            Record(item)
            for item in self.get("@hierarchy.0", default=())
            if item.get("identifier")
        )

    @cached_property
    def next_record(self) -> Union["Record", None]:
        if next := self.get("@next", default=None):
            return Record(next)

    @cached_property
    def previous_record(self) -> Union["Record", None]:
        if prev := self.get("@previous", default=None):
            return Record(prev)

    @cached_property
    def topics(self) -> Tuple[Dict[str, str]]:
        return_value = []
        for item in self.get("topic", default=()):
            topic_title = ""
            try:
                topic_title = item.get["name"][0]["value"]
            except (KeyError, IndexError):
                topic_title = extract(item, "summary.title")
            if topic_title:
                return_value.append({"title": topic_title})
        return tuple(return_value)

    @cached_property
    def related_records(self) -> Tuple["Record"]:
        return tuple(
            Record(item)
            for item in self.get("related", default=())
            if extract(item, "@link.relationship.value", default="") == "related"
        )

    @cached_property
    def related_articles(self) -> Tuple["Record"]:
        return tuple(
            Record(item)
            for item in self.get("related", default=())
            if item.get("summary")
            and extract(item, "@admin.source", default="") == "wagtail-es"
        )

    @cached_property
    def related_materials(self) -> Tuple[Dict[str, Any]]:
        return tuple(
            dict(
                description=item.get("description", ""),
                links=list(format_link(val) for val in item.get("links", ())),
            )
            for item in self.template.get("relatedMaterials", ())
        )

    @cached_property
    def custom_record_type(self) -> str:
        if source := self.source:
            return source
        else:
            identifier = self.get("identifier", ())
            if find(identifier, predicate=lambda i: i["type"] == "faid"):
                return "CREATORS"
        return ""

    def get_gtm_content_group(self) -> str:
        """
        Overrides DataLayerMixin.get_gtm_content_group() to
        return content group otherwise the name of the class.
        """
        if self.source == "CAT":
            return "Catalogue: The National Archives"
        elif self.source == "ARCHON":
            return "Catalogue: Archive Details"
        elif self.source:
            return "Catalogue: Other Archive Records"
        else:
            return self.__class__.__name__

    @property
    def custom_dimension_11(self) -> str:
        if self.repo_archon_value and self.repo_summary_title:
            return self.repo_archon_value + " - " + self.repo_summary_title
        else:
            return "Held by not available"

    @property
    def custom_dimension_12(self) -> str:
        if self.level_code and self.level:
            return f"Level {self.level_code} - {self.level}"
        return ""

    @property
    def custom_dimension_13(self) -> str:
        for ancestor in self.hierarchy:
            if (
                ancestor.level_code == 3
                and ancestor.reference_number
                and ancestor.summary_title
            ):
                return f"{ancestor.reference_number} - {ancestor.summary_title}"
        return ""

    @property
    def custom_dimension_14(self) -> str:
        if self.reference_number and self.summary_title:
            return f"{self.reference_number} - {self.summary_title}"
        return ""

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Returns data to be included in the Google Analytics datalayer when
        rendering this record.

        Override this method on subclasses to add data that is relevant to a
        specific record type.
        """

        data = super().get_datalayer_data(request)
        data.update(
            contentGroup1=self.get_gtm_content_group(),
            customDimension3="record detail",
            customDimension11=self.custom_dimension_11,
            customDimension12=self.custom_dimension_12,
            customDimension13=self.custom_dimension_13,
            customDimension14=self.custom_dimension_14,
            customDimension15=self.source,
            customDimension16=self.availability_condition_category,
            customDimension17=self.delivery_option,
        )
        return data

    @cached_property
    def title(self) -> str:
        return mark_safe(self.template.get("title", ""))

    @cached_property
    def archive_contact_info(self) -> Optional[ContactInfo]:
        """
        Extracts data from the api "_source.description" attribute if available.
        Then transforms that data to be represented by ContactInfo.
        The data is extracted from html tags that are stored in the 'value' attribute.
        These tags are fixed and only for this method.

        Returns ContactInfo or None if data is not available.
        """
        contact_info = None
        for description in self.get("description", ()):
            if value := description.get("ephemera", {}).get("value", ""):
                # convert to lower case for extraction
                value = value.replace("mapURL", "mapurl")
                value = value.replace("jobTitle", "jobtitle")
                value = value.replace("firstName", "firstname")
                value = value.replace("lastName", "lastname")
                document = pq(value)
                contact_info = ContactInfo(
                    address_line1=document("addressline1").text(),
                    address_town=document("addresstown").text(),
                    postcode=document("postcode").text(),
                    address_country=document("addresscountry").text(),
                    map_url=document("mapurl").text(),
                    url=document("url").text(),
                    telephone=document("telephone").text(),
                    fax=document("fax").text(),
                    email=document("email").text(),
                    corresp_addr=document("correspaddr").text(),
                    contact_job_title=document("jobtitle").text(),
                    contact_title=document("title").text(),
                    contact_first_name=document("firstname").text(),
                    contact_last_name=document("lastname").text(),
                )
        return contact_info

    @cached_property
    def archive_further_info(self) -> Optional[FurtherInfo]:
        """
        Extracts data from the api "_source.place" attribute if available.
        Then transforms that data to be represented by FurtherInfo.
        The data is extracted from html tags that are stored in the 'value' attribute.
        These tags are fixed and only for this method.

        Returns FurtherInfo or None if data is not available.
        """
        further_info = None
        for place in self.get("place", ()):
            if value := place.get("description", {}).get("value", ""):
                document = pq(value)
                # remove empty values
                facilities = list(
                    filter(
                        None,
                        [
                            document("disabledaccess").text(),
                            document("researchservice").text(),
                            document("appointment").text(),
                            document("ticket").text(),
                            document("idrequired").text(),
                            document("fee").text(),
                        ],
                    )
                )
                further_info = FurtherInfo(
                    opening_hours=mark_safe(document("openinghours").text()),
                    holidays=document("holidays").text(),
                    facilities=facilities,
                    comments=mark_safe(document("comments").text()),
                )
        return further_info

    def _get_trasformed_archive_record_creators_info(
        self, collection_name
    ) -> Optional[CollectionInfo]:
        """
        Extracts data from the api "_source.links" attribute if available. It holds record creators info.
        Then transforms that data to be represented by CollectionInfo.

        Returns CollectionInfo or None if data is not available.
        """
        collection_info = None
        if archive_links := self.get("links", ()):
            filtered_values = find_all(
                archive_links,
                predicate=lambda i: i["identifier"][0]["value"]
                == collection_name.get("api_links_indentifier_value"),
            )
            info_list = []
            for item in filtered_values:
                info_dict = {
                    "summary_title": item.get("summary", {}).get("title", ""),
                    "place": item.get("place", {})
                    .get("name", [{}])[0]
                    .get("value", ""),
                }

                if admin_id := item.get("@admin", {}).get("id", ""):
                    # update url only when id is available
                    try:
                        info_dict.update(
                            {
                                "url": reverse(
                                    "details-page-machine-readable",
                                    kwargs={"iaid": admin_id},
                                )
                            }
                        )
                    except NoReverseMatch:
                        logger.debug(
                            f"_get_trasformed_archive_record_creators_info:No reverse match for details-page-machine-readable with admin_id = {admin_id}"
                        )

                info_list.append(info_dict)

            if info_list:
                collection_info = CollectionInfo(
                    name=collection_name.get("name"),
                    display_name=collection_name.get("display_name"),
                    long_display_name=collection_name.get("long_display_name"),
                    count=len(info_list),
                    info_list=info_list,
                )

        return collection_info

    def _get_transformed_archive_nra_records_info(
        self, collection_name
    ) -> Optional[CollectionInfo]:
        """
        Extracts data from the api "_source.manifestations" attribute if available. It holds nra records info.
        Then transforms that data to be represented by CollectionInfo.

        Returns CollectionInfo or None if data is not available.
        """
        collection_info = None
        if manifestations := self.get("manifestations", ()):
            info_list = []
            for item in manifestations:
                info_list.append(
                    {
                        "identifier_title": f'NRA {item.get("identifier", [{}])[0].get("value", "")} {item.get("title", [{}])[0].get("value", "")}',
                        "url": item.get("url", ""),
                    }
                )
            if info_list:
                collection_info = CollectionInfo(
                    name=collection_name.get("name"),
                    display_name=collection_name.get("display_name"),
                    long_display_name=collection_name.get("long_display_name"),
                    count=len(info_list),
                    info_list=info_list,
                )

        return collection_info

    @cached_property
    def archive_collections(self) -> ArchiveCollections:
        """
        Combines record creators info and nra records info as both have similar structure representations.
        The combined data is is then represented by ArchiveCollections.

        Returns archive collection info for record creators and nra records
        """
        # NOTE: this is the specicfic order of these list record creators and nra records
        collection_info_list = [
            self._get_trasformed_archive_record_creators_info(collection)
            for collection in ARCHIVE_RECORD_CREATORS_COLLECTION
        ]
        collection_info_list.extend(
            [
                self._get_transformed_archive_nra_records_info(collection)
                for collection in ARCHIVE_NRA_RECORDS_COLLECTION
            ]
        )

        archive_collections = ArchiveCollections(
            # remove empty values
            collection_info_list=[
                item for item in collection_info_list if item is not None
            ]
        )
        return archive_collections

    @cached_property
    def archive_accessions(self) -> Optional[AccessionsInfo]:
        """
        Extracts data from the api "_source.@template.accumulationDates" attribute if available.
        Then transforms that data to be represented by AccessionsInfo.
        The data is extracted from html tags that are stored with the 'accumulationDates' attribute.
        These tags are fixed and only for this method.

        Returns AccessionsInfo or None if data is not available.
        """
        accessions_info = None
        if accumulation_dates := self.template.get("accumulationDates", ""):
            document = pq(accumulation_dates)
            # extract year as a list of strings
            year_list = document.find("accessionyear").text().split()
            accession_years = {}
            for year in year_list:
                # transfrom year values {year:url}
                accession_years.update(
                    {
                        year: f"{TNA_URLS.get('tna_accessions')}/{year}/{year[2:]}returns/{year[2:]}ac{self.reference_number}.htm"
                    }
                )
            accessions_info = AccessionsInfo(
                accession_years=accession_years,
            )
        return accessions_info

    @cached_property
    def archive_repository_url(self) -> str:
        return self.get("repository.url", "")

    @cached_property
    def alternative_names(self) -> tuple(dict):
        alternative_names = ()
        if names := self.get("name", ()):
            for item in names:
                if type := item.get("type", ""):
                    if type in (
                        "maiden name",
                        "also known as",
                        "formerly known as",
                        "later known as",
                        "pseudonym",
                        "relation of",
                        "real name",
                        "standardised form of name according to other rules",
                    ):
                        alternative_names += (
                            {
                                "label": type.capitalize(),
                                "value": item.get("value", ""),
                            },
                        )
                    elif type == "unknown / other":
                        alternative_names += (
                            {
                                "label": type.title(),
                                "value": item.get("value", ""),
                            },
                        )

        return alternative_names

    @cached_property
    def first_name(self) -> str:
        first_name = ""
        if name_data := self.get("name", ()):
            for item in name_data:
                if first_name_list := item.get("first_name"):
                    first_name = " ".join(first_name_list)
        return first_name

    @cached_property
    def last_name(self) -> str:
        if name_data := self.get("name", ()):
            for item in name_data:
                if last_name := item.get("last_name", ""):
                    return last_name
        return ""

    @cached_property
    def title_prefix(self) -> str:
        if name_data := self.get("name", ()):
            for item in name_data:
                if title_prefix := item.get("title_prefix"):
                    return title_prefix
        return ""

    @cached_property
    def title_for_name(self) -> str:
        if name_data := self.get("name", ()):
            for item in name_data:
                if title := item.get("title"):
                    return title
        return ""

    @cached_property
    def gender(self) -> str:
        if gender := self.get("gender", ""):
            if gender == "M":
                return "Male"
            elif gender == "F":
                return "Female"
            logger.debug(
                f"Gender value={gender} could not be translated for iaid={self.iaid}"
            )
        return gender

    @cached_property
    def history(self) -> str:
        if description := self.get("description", ()):
            for item in description:
                if item.get("type") == "history":
                    if value := item.get("value", ""):
                        return mark_safe(value)
        return ""

    @cached_property
    def biography(self) -> dict:
        if description := self.get("description", ()):
            for item in description:
                if item.get("type") == "biography":
                    return {
                        "value": item.get("value", ""),
                        "url": item.get("url", ""),
                    }
        return {}

    @cached_property
    def func_occup_activ(self) -> str:
        if description := self.get("description", ()):
            for item in description:
                if item.get("type") == "functions, occupations and activities":
                    if value := item.get("value", ""):
                        document = pq(value)
                        for tag in ("foa", "function"):
                            if doc_value := document(tag).text():
                                return doc_value
                        return value
        return ""

    @cached_property
    def places(self) -> tuple(str):
        places = ()
        if place := self.get("place", ()):
            for item in place:
                if name := item.get("name", ()):
                    for item in name:
                        if value := item.get("value", ""):
                            places += (value,)
        return places

    @cached_property
    def birth_date(self) -> str:
        return extract(self.get("birth", {}), "date.value", default="")

    @cached_property
    def death_date(self) -> str:
        return extract(self.get("death", {}), "date.value", default="")

    @cached_property
    def start_date(self) -> str:
        if date := extract(self.get("start", {}), "date", default=()):
            for item in date:
                if value := item.get("value", ""):
                    return value
        return ""

    @cached_property
    def end_date(self) -> str:
        if date := extract(self.get("end", {}), "date", default=()):
            for item in date:
                if value := item.get("value", ""):
                    return value
        return ""

    @cached_property
    def record_creators_date(self) -> str:
        """
        Returns dates for person, person's activity/service,  both, or any if available
        """
        separator = "-"
        joiner = "; "
        person_date = service_activity_date = ""
        if self.birth_date and self.death_date:
            person_date = f"{self.birth_date}{separator}{self.death_date}"
        else:
            person_date = self.birth_date or self.death_date

        if self.start_date and self.end_date:
            service_activity_date = f"{self.start_date}{separator}{self.end_date}"
        else:
            service_activity_date = self.start_date or self.end_date

        # return self.birth_date or self.death_date or self.start_date or self.end_date
        if person_date and service_activity_date:
            return joiner.join([person_date, service_activity_date])

        return person_date or service_activity_date

    @cached_property
    def name_authority_reference(self) -> str:
        if identifier := self.get("identifier", ()):
            for item in identifier:
                if name_authority_reference := item.get("name_authority_reference", ""):
                    return name_authority_reference
        return ""

    @cached_property
    def former_name_authority_reference(self) -> str:
        if identifier := self.get("identifier", ()):
            for item in identifier:
                if former_name_authority_reference := item.get(
                    "former_name_authority_reference", ""
                ):
                    return former_name_authority_reference
        return ""

    @cached_property
    def closure_status(self) -> str:
        return extract(self.get("@template", {}), "details.closureStatus", default="")

    @cached_property
    def creator(self) -> list(str):
        return self.template.get("creator", [])

    @cached_property
    def dimensions(self) -> str:
        return self.template.get("dimensions", "")

    @cached_property
    def former_department_reference(self) -> str:
        return self.template.get("formerDepartmentReference", "")

    @cached_property
    def former_pro_reference(self) -> str:
        return self.template.get("formerProReference", "")

    @cached_property
    def language(self) -> list(str):
        return self.template.get("language", [])

    @cached_property
    def map_designation(self) -> str:
        return mark_safe(self.template.get("mapDesignation", ""))

    @cached_property
    def map_scale(self) -> str:
        return self.template.get("mapScale", "")

    @cached_property
    def note(self) -> list(str):
        notes = [mark_safe(note) for note in self.template.get("note", [])]
        return notes

    @cached_property
    def physical_condition(self) -> str:
        return self.template.get("physicalCondition", "")

    @cached_property
    def physical_description(self) -> str:
        return self.template.get("physicalDescription", "")

    @cached_property
    def accruals(self) -> str:
        return self.template.get("accruals", "")

    @cached_property
    def accumulation_dates(self) -> str:
        return self.template.get("accumulationDates", "")

    @cached_property
    def appraisal_information(self) -> str:
        return self.template.get("appraisalInformation", "")

    @cached_property
    def immediate_source_of_acquisition(self) -> list(str):
        return self.template.get("immediateSourceOfAcquisition", [])

    @cached_property
    def administrative_background(self) -> str:
        return mark_safe(self.template.get("administrativeBackground", ""))

    @cached_property
    def separated_materials(self) -> Tuple[Dict[str, Any]]:
        return tuple(
            dict(
                description=item.get("description", ""),
                links=list(format_link(val) for val in item.get("links", ())),
            )
            for item in self.template.get("separatedMaterials", ())
        )

    @cached_property
    def unpublished_finding_aids(self) -> list(str):
        return self.template.get("unpublishedFindingAids", [])

    @cached_property
    def copies_information(self) -> list(str):
        return self.template.get("copiesInformation", [])

    @cached_property
    def custodial_history(self) -> str:
        return self.template.get("custodialHistory", "")

    @cached_property
    def location_of_originals(self) -> list(str):
        return self.template.get("locationOfOriginals", [])

    @cached_property
    def restrictions_on_use(self) -> str:
        return self.template.get("restrictionsOnUse", "")

    @cached_property
    def publication_note(self) -> list(str):
        return self.template.get("publicationNote", [])


@dataclass
class Image:
    """Represents an image item returned by Client API."""

    location: str
    # Sort position of this image. Used to create the image-viewer URL
    # and to fetch this particular image from a series of images.
    # sort is an str that contains an int with a leading zero if less
    # than ten.
    sort: str
    thumbnail_location: str

    @property
    def thumbnail_url(self):
        """Use thumbnail URL is available, otherwise fallback to image-serve."""
        if self.thumbnail_location:
            return f"{settings.IMAGE_PREVIEW_BASE_URL}{self.thumbnail_location}"
        elif self.location:
            return reverse("image-serve", kwargs={"location": self.location})
