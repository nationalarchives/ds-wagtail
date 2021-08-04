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


def datalayer_data(page) -> dict:
    """
    Return Datalayer data for a Page object.

    https:#developers.google.com/tag-manager/devguide
    """

    return {
        "contentGroup1": getContentGroup(page),         # The name of the content group - [Always has a value]
		"customDimension1": "offsite",                  # The reader type (options are "offsite", "onsite_public", "onsite_staff", "subscription")
		"customDimension2": "",                         # The user type and is private beta specific - the user ID for participants. Left blank in this example because format unknown.
		"customDimension3": page.get_verbose_name(),    # The page type - [Always has a value]
    }

register.filter("datalayer_data", datalayer_data)
