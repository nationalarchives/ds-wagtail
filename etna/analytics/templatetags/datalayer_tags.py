from django import template
from django.conf import settings

register = template.Library()


def get_content_group(page):
    """
    Get the content group name for a specified page.

    The group name is derived from the page model's app name.

    If the model has no defined group, the page title is returned by default.
    """
    appname = page.__module__.split(".")[1]
    groups = {
        "home": "Homepage",
        "insights": "Insights",
        "collections": "Explorer",
        "records": "TNA catalogue",
    }
    return groups.get(appname, page.title)


def get_availability_condition(page):
    """
    Return the page's availablility condition value (if applicable).
    """
    try:
        return page.availablility_delivery_condition
    except AttributeError:
        return ""


def get_availability_condition_category(page):
    """
    Return a category for the availability condition of the page.

    If an availability condition is not present, return an empty string.
    """
    availability_condition = get_availability_condition(page)

    return settings.AVAILABILITY_CONDITION_CATEGORIES.get(availability_condition, "")


@register.filter
def datalayer(page, request) -> dict:
    """
    Return Datalayer data for a Page object.

    https://developers.google.com/tag-manager/devguide
    """

    return {
        # Name of the content group - [Always has a value]
        "contentGroup1": get_content_group(page),
        # The reader type (options are "offsite",
        # "onsite_public", "onsite_staff", "subscription")
        "customDimension1": "offsite",
        # - User ID for participants.
        "customDimension2": request.user.id,
        # Page type - [Always has a value]
        "customDimension3": page.get_verbose_name(),
        # Taxonomy topics for the page, delineated by semi-colons. Empty string if no value.
        "customDimension4": "",
        # Taxonomy sub topic where applicable. Empty string if not applicable.
        "customDimension5": "",
        # Taxonomy term where applicable. Empty string if not applicable.
        "customDimension6": "",
        # Time period where applicable. Empty string if not applicable.
        "customDimension7": "",
        # Sub time period where applicable. Empty string if not applicable.
        "customDimension8": "",
        # Entity type where applicable. Empty string if not applicable.
        "customDimension9": "",
        # Entity label where applicable. Empty string if not applicable.
        "customDimension10": "",
        # Catalogue repository where applicable. Empty string if not applicable.
        "customDimension11": "",
        # Catalogue level where applicable. Empty string if not applicable.
        "customDimension12": "",
        # Catalogue series where applicable. Empty string if not applicable.
        "customDimension13": "",
        # Catalogue reference where applicable. Empty string if not applicable.
        "customDimension14": "",
        # CatalogueDataSource where applicable. Empty string if not applicable.
        "customDimension15": "",
        # Availability condition category where applicable.  Empty string if not applicable.
        "customDimension16": get_availability_condition_category(page),
        # Availability condition where applicable.  Empty string if not applicable.
        "customDimension17": get_availability_condition(page),
    }


@register.simple_tag(takes_context=True)
def image_browse_datalayer(context) -> dict:
    """Custom tag for image browse datalayer.

    Image browse isn't a page served by Wagtail, therefore we're unable to
    query the page object to populate the datalayer.
    """
    return {
        "contentGroup1": "TNA catalogue",
        "customDimension1": "offsite",
        # The user type and is private beta specific - the user ID for participants.
        "customDimension2": context["request"].user.id,
        "customDimension18": context.get("images_count", ""),
    }
