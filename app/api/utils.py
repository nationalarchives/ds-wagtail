from wagtail.api.v2.utils import BadRequestError
from wagtail.models import Site


def get_site_from_request(request):
    """
    Get the site based on the request. Checks site parameter or falls back to default
    site if not found.

    Args:
        request: The Django request object

    Returns:
        Site: The Wagtail Site object, or None if no site is configured

    Raises:
        BadRequestError: If site parameter is invalid or ambiguous
    """
    # Check if we have a specific site to look for
    if "site" in request.GET:
        # Optionally allow querying by port
        if ":" in request.GET["site"]:
            (hostname, port) = request.GET["site"].split(":", 1)
            query = {
                "hostname": hostname,
                "port": port,
            }
        else:
            query = {
                "hostname": request.GET["site"],
            }
        try:
            site = Site.objects.get(**query)
        except Site.MultipleObjectsReturned:
            raise BadRequestError(
                "Your query returned multiple sites. Try adding a port number to your site filter."
            )
        except Site.DoesNotExist:
            return None
    else:
        # Otherwise, use the default site
        try:
            site = Site.objects.get(is_default_site=True)
        except Site.DoesNotExist:
            return None

    return site
