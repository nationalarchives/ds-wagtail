from django.utils.decorators import method_decorator

from wagtail.core.models import Page

from etna.core.cache_control import (
    apply_default_cache_control,
    apply_default_vary_headers,
)

__all__ = [
    "BasePage",
]


@method_decorator(apply_default_vary_headers, name="serve")
@method_decorator(apply_default_cache_control, name="serve")
class BasePage(Page):
    """
    An abstract base model that is used for all Page models within
    the project. Any common fields, Wagtail overrides or custom
    functionality can be added here.
    """

    class Meta:
        abstract = True
