from django import template
from django.conf import settings

from ...ciim.constants import TNA_URLS, LevelKeys, NonTNALevelKeys
from ..field_labels import FIELD_LABELS
from ..models import Record

register = template.Library()


@register.simple_tag
def record_url(
    record: Record,
    is_editorial: bool = False,
    order_from_discovery: bool = False,
    level_or_archive: str = "",
    base_record: Record = None,
    form_group: str = "",
    use_non_reference_number_url: bool = True,
    use_collection_id: bool = False,
) -> str:
    """
    Return the URL for the provided `record`, which should always be a
    fully-transformed `etna.records.models.Record` instance.

    use_non_reference_number_url: this serves one stop switch

    level_or_archive: Use api level name or "Archive" name. This value is checked
    with a set of values in order to override reference number that show
    disambiguation page (multiple iaid share the same reference number).

    base_record: is the original record; use when record is not the original record
    and record is a subset of the original record along with level_or_archive
    in order to determine reference number override

    form_group: use with results from search queries, value determines ex: community, tna, nonTna results
    """
    if form_group == "community" or record.group == "community":
        if use_collection_id:
            return record.get_collection_url
        return record.get_ciim_url

    if is_editorial and settings.FEATURE_RECORD_LINKS_GO_TO_DISCOVERY and record.iaid:
        return TNA_URLS.get("discovery_rec_default_fmt").format(id=record.iaid)

    if order_from_discovery:
        return TNA_URLS.get("discovery_rec_default_fmt").format(id=record.iaid)

    if record:
        if use_non_reference_number_url:
            return record.non_reference_number_url

        if form_group == "nonTna":
            is_tna = False
        elif form_group == "tna":
            is_tna = True
        else:
            is_tna = record.is_tna

            if base_record:
                is_tna = base_record.is_tna

        if is_tna:
            reference_number_override_list = [
                "Lettercode",  # same as Department, but returned in API response
                level_name(level_code=1, is_tna=is_tna),
                level_name(level_code=2, is_tna=is_tna),
                level_name(level_code=4, is_tna=is_tna),
                level_name(level_code=5, is_tna=is_tna),
                "Archive",  # no level specified for this value
            ]
        else:
            reference_number_override_list = [
                level_name(level_code=1, is_tna=is_tna),
                level_name(level_code=9, is_tna=is_tna),
                level_name(level_code=10, is_tna=is_tna),
                level_name(level_code=11, is_tna=is_tna),
                "Archive",  # no level specified for this value
            ]

        if level_or_archive in reference_number_override_list:
            return record.non_reference_number_url
        else:
            return record.url
    return ""


@register.simple_tag
def is_page_current_item_in_hierarchy(page: Record, hierarchy_item: Record):
    """Checks whether given page matches item from a record's hierarchy"""
    return page.iaid == hierarchy_item.iaid


@register.filter
def as_label(record_field_name: str) -> str:
    """returns human readable label for pre configured record field name, otherwise Invalid name"""
    return FIELD_LABELS.get(record_field_name, "UNRECOGNISED FIELD NAME")


@register.simple_tag
def level_name(level_code: int, is_tna: bool) -> str:
    """returns level as a human readable string"""
    if is_tna:
        return LevelKeys["LEVEL_" + str(level_code)].value
    else:
        return NonTNALevelKeys["LEVEL_" + str(level_code)].value


@register.simple_tag
def breadcrumb_items(hierarchy: list, is_tna: bool, current_record: Record) -> list:
    """Returns breadcrumb items depending on position in hierarchy
    Update tna_breadcrumb_levels or oa_breadcrumb_levels to change the levels displayed
    """
    items = []
    tna_breadcrumb_levels = [1, 2, 3]
    oa_breadcrumb_levels = [1, 2, 5]
    for hierarchy_record in hierarchy:
        if hierarchy_record.level_code != current_record.level_code:
            if is_tna:
                if hierarchy_record.level_code in tna_breadcrumb_levels:
                    items.append(hierarchy_record)
            else:
                if hierarchy_record.level_code in oa_breadcrumb_levels:
                    items.append(hierarchy_record)
    items.append(current_record)
    if len(items) > 3:
        items = items[-3:]
    return items
