from django import template


register = template.Library()


def getContentGroup(page):
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
        # TODO: Update with actual attribute name when available
        return  page.availability_condition
    except AttributeError:
        return ""


def get_availability_condition_category(page):
    """
    Return a category for the availability condition of the page.

    If an availability condition is not present, return an empty string.
    """

    availability_condition = get_availability_condition(page)
    categories = {
        "AcademicSubscription": "Academic Subscription",
        "AccessUnderReview": "Not Viewable online",
        "AV_Media": "Viewable online",
        "ClosedFOIReview": "Not viewable online",
        "ClosedRetainedDeptKnown": "Not viewable online",
        "ClosedRetainedDeptUnKnown": "Not viewable online",
        "CollectionCare": "Not viewable online",
        "DigitizedAvailableButNotDownloadableAtItemLevel": "Not viewable online",
        "DigitizedAvailableButNotDownloadableAtPieceLevel": "Not viewable online",
        "DigitizedDiscovery - Free": "Viewable online",
        "DigitizedDiscovery - Charged": "Viewable online",
        "DigitizedDiscovery - Charged (+LIAs)": "Viewable online & via 3rd party",
        "DigitizedLIA": "Viewable via 3rd party",
        "DigitizedOther": "Viewable online",
        "DigitizedPartiallyOpened": "Not used",
        "DisplayAtMuseum": "Not viewable online",
        "FileAuthority": "Not viewable online",
        "GovtWebArchive": "Viewable via 3rd party",
        "ImageLibrary": "Viewable via 3rd party",
        "InUse": "Not viewable online",
        "InvigilationSafeRoom": "Not viewable online",
        "LocalArchive": "Not viewable online",
        "MissingLost": "Not viewable online",
        "MouldTreatment": "Not viewable online",
        "Offsite": "Not viewable online",
        "Onloan": "Not viewable online",
        "OrderException": "Error",
        "OrderOriginal": "Not viewable online",
        "PaidSearch": "Not viewable online",
        "Surrogate": "Not viewable online",
        "TooLargeToCopyOffsite": "Not viewable online",
        "TooLargeToCopyOriginal": "Not viewable online",
        "TooLargeToCopySurrogate": "Not viewable online",
        "Unavailable": "Not viewable online",
        "Unfit": "Not viewable online",
    }
    return categories.get(availability_condition, "")


def get_user_info(user):
    if user.is_authenticated:
        return user.email
    else:
        return "anonymous"


def datalayer_data(page, user) -> dict:
    """
    Return Datalayer data for a Page object.

    https:#developers.google.com/tag-manager/devguide
    """

    return {
        "contentGroup1": getContentGroup(page),         # The name of the content group - [Always has a value]
        "customDimension1": "offsite",                  # The reader type (options are "offsite", "onsite_public", "onsite_staff", "subscription")
        "customDimension2": get_user_info(user),        # The user type and is private beta specific - the user ID for participants. Left blank in this example because format unknown.
        "customDimension3": page.get_verbose_name(),    # The page type - [Always has a value]
        'customDimension4': "",     # Taxonomy topics for the page, delineated by semi-colons. Empty string if no value.
        'customDimension5': "",     # This is the taxonomy sub topic where applicable. Empty string if not applicable.
        'customDimension6': "",     # This is the taxonomy term where applicable. Empty string if not applicable.
        'customDimension7': "",     # This is the time period where applicable. Empty string if not applicable.
        'customDimension8': "",     # This is the sub time period where applicable. Empty string if not applicable.
        'customDimension9': "",     # This is the entity type where applicable. Empty string if not applicable.
        'customDimension10': "",    # This is the entity label where applicable. Empty string if not applicable.
        'customDimension11': "",    # This is the catalogue repository where applicable. Empty string if not applicable.
        'customDimension12': "",    # This is the catalogue level where applicable. Empty string if not applicable.
        'customDimension13': "",    # This is the catalogue series where applicable. Empty string if not applicable.
        'customDimension14': "",    # This is the catalogue reference where applicable. Empty string if not applicable.
        'customDimension15': "",    # This is the catalogueDataSource where applicable. Empty string if not applicable.
        'customDimension16': get_availability_condition_category(page), # This is the availability condition category where applicable. Empty string if not applicable.
        'customDimension17': get_availability_condition(page),          # This is the availability condition where applicable. Empty string if not applicable.
        'customDimension18': "",    # The number of images shown in browse where applicable. Empty string if not applicable.
    }

register.filter("datalayer_data", datalayer_data)
