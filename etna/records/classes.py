from dataclasses import dataclass, field
from typing import List


@dataclass
class ContactInfo:
    address_line1: str = ""
    address_town: str = ""
    postcode: str = ""
    address_country: str = ""
    map_url: str = ""
    url: str = ""
    telephone: str = ""
    fax: str = ""
    email: str = ""
    corresp_addr: str = ""
    contact_job_title: str = ""
    contact_title: str = ""
    contact_first_name: str = ""
    contact_last_name: str = ""


@dataclass
class FurtherInfo:
    opening_hours: str = ""
    holidays: str = ""
    facilities: List[str] = field(default_factory=list)
    comments: str = ""


@dataclass
class CollectionInfo:
    name: str = ""
    display_name: str = ""
    long_display_name: str = ""
    count: int = 0
    info_list: List[dict] = field(default_factory=list)


@dataclass
class ArchiveCollections:
    collection_info_list: List = field(default_factory=list)


@dataclass
class AccessionsInfo:
    # the dict value is held in the format {year:url}
    accession_years: dict = field(default_factory=dict)
