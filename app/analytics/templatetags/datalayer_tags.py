from django import template

register = template.Library()


@register.inclusion_tag("includes/gtm-datalayer.html", takes_context=True)
def render_gtm_datalayer(context, obj) -> dict:
    """
    Render the datalayer for an instance of a ``DataLayerMixin`` subclass.
    https://developers.google.com/tag-manager/devguide
    """
    try:
        data = obj.get_datalayer_data(context["request"])
    except AttributeError:
        data = {}

    # Add a json serialized version of the data for output
    return {"data": data}


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
