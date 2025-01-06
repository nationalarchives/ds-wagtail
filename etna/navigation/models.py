from typing import Sequence

from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.models import Orderable, Page
from wagtail.query import PageQuerySet

from .widgets import NamedURLSelect


class MenuItem:
    """
    A class that can be used as a base for in-memory OR Django models
    that can be used to represent menu items.
    """

    label = ""
    page = None
    url_name = ""
    menu = None
    request = None

    def bind_to_request(self, request: HttpRequest) -> "MenuItem":
        """
        This is method is called immediately after looking up the relevant menu
        and items from the database for the current ``request``. The value is
        used by ``url()`` to improve the efficiency of Wagtail page URL
        generation, and by ``is_active()`` to determine whether the item should
        be marked as 'active' in the template.
        """
        self.request = request
        return self

    @cached_property
    def is_site_root_item(self):
        return self.page and self.page.is_site_root()

    @cached_property
    def url(self):
        try:
            return self.page.specific_deferred.get_url(request=self.request)
        except AttributeError:
            pass
        try:
            return reverse(self.url_name)
        except NoReverseMatch:
            pass
        return "#"

    @cached_property
    def is_active(self):
        if self.request:
            if self.is_site_root_item:
                return self.request.path in ("", "/")
            return self.request.path.startswith(self.url)
        return False

    def get_child_pages(self) -> PageQuerySet:
        if not self.page or self.is_site_root_item:
            return Page.objects.none()
        return (
            Page.objects.live()
            .in_menu()
            .child_of(self.page)
            .defer_streamfields()
            .specific()
        )

    @cached_property
    def children(self) -> Sequence["MenuItem"]:
        """
        Return a list of ``MenuItem`` objects that can be used to render
        links for 'child pages' of this item.
        """
        items = []
        for child in self.get_child_pages():
            menu_item = MenuItem()
            menu_item.page = child
            menu_item.label = child.title
            menu_item.menu = self.menu
            menu_item.bind_to_request(self.request)
            items.append(menu_item)
        return items

    @property
    def has_children(self) -> bool:
        return bool(self.children)


class AbstractMenuItem(MenuItem, Orderable):
    """
    An abstract Model class that can be built upon to represent/store
    menu item details for a specific ``AbstractMenuModel`` subclass.
    """

    label = models.CharField(
        verbose_name="label",
        max_length=50,
    )
    page = models.ForeignKey(
        Page,
        verbose_name="link to a page",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    url_name = models.CharField(
        verbose_name="OR a fixed URL",
        max_length=255,
        blank=True,
    )

    class Meta(Orderable.Meta):
        abstract = True

    panels = [
        FieldPanel("label"),
        FieldPanel("page"),
        FieldPanel("url_name", widget=NamedURLSelect),
    ]

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        try:
            page = self.page
        except Page.DoesNotExist:
            page = None
        if not self.url_name and not page:
            msg = _("Please choose a page or select a fixed URL to link to.")
            raise ValidationError({"page": msg})
        if self.url_name and page:
            msg = _("Linking to both a page and fixed URL is not permitted.")
            raise ValidationError({"page": msg, "url_name": msg})
        if page and not page.live:
            msg = _("Only published pages can be selected as menu items.")
            raise ValidationError({"page": msg})
