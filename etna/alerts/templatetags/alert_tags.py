from django import template

from wagtail.core.models import Page

from ..models import Alert

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


@register.inclusion_tag('alerts/tags/alerts.html', takes_context=False)
def alerts(page):
    """
    Return alerts from current page as well as those cascaded from ancestors.
    """
    alerts = []

    # Get alert for current page, if any.
    alert = get_page_alert(page)
    if alert:
        alerts.insert(0, alert)

    # Get current page ancestors.
    branch = Page.objects.ancestor_of(page).specific()
    # Iterate backwards and, if page has alert and "cascade" is true,
    # add to alerts list.
    for i in reversed(range(branch.count())):
        alert = get_page_alert(branch[i])
        if alert and alert.cascade:
            alerts.insert(0, alert)

    return {
        'alerts': alerts
    }
