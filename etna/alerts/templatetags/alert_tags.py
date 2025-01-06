from django import template
from wagtail.models import Page

# Alert snippets

register = template.Library()


def get_page_alert(page):
    """
    Get the alert field from page, if it exists.
    """
    alert = None
    try:
        alert = page.alert
    except AttributeError:
        pass

    if alert and alert.active:
        return alert
    else:
        return None


@register.inclusion_tag("alerts/tags/alerts.html")
def alerts(page):
    """
    Return alerts from current page as well as those cascaded from ancestors.
    """

    if not page:
        # Return early if no page is passed to tag
        # This can happen on view-based pages like the record disambiguation page.
        return None

    alerts = []

    # Iterate through current page ancestors.
    # If page has alert and "cascade" is true, add to alerts list.
    for ancestor in Page.objects.ancestor_of(page).specific():
        alert = get_page_alert(ancestor)
        if alert and alert.cascade:
            alerts.append(alert)

    # Get alert for current page, if any.
    # This needs to be done separately because cascade might not be set.
    alert = get_page_alert(page)
    if alert:
        alerts.append(alert)

    return {"alerts": alerts}
