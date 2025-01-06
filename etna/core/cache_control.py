from django.conf import settings
from django.views.decorators.cache import cache_control
from django.views.decorators.vary import vary_on_headers


def get_default_cache_control_kwargs():
    """
    Get cache control parameters used by the cache control decorators
    used by default on most pages. These parameters are meant to be
    sane defaults that can be applied to a standard content page.
    """
    s_maxage = getattr(settings, "CACHE_CONTROL_S_MAXAGE", None)
    stale_while_revalidate = getattr(
        settings, "CACHE_CONTROL_STALE_WHILE_REVALIDATE", None
    )
    cache_control_kwargs = {
        "s_maxage": s_maxage,
        "stale_while_revalidate": stale_while_revalidate,
        "public": True,
    }
    return {k: v for k, v in cache_control_kwargs.items() if v is not None}


apply_default_cache_control = cache_control(
    **get_default_cache_control_kwargs()
)

apply_default_vary_headers = vary_on_headers(
    "Cookie", "X-Requested-With", "X-Forwarded-Proto", "Accept-Encoding"
)
