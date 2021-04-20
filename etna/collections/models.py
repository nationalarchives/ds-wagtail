from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page


class ExplorerPage(Page):
    """Collection Explorer landing page."""

    introduction = models.CharField(max_length=200, blank=False)

    content_panels = Page.content_panels + [FieldPanel("introduction")]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["collections.CategoryPage"]


class CategoryPage(Page):
    """Category page."""

    introduction = models.CharField(max_length=200, blank=False)

    content_panels = Page.content_panels + [FieldPanel("introduction")]

    parent_page_types = ["collections.ExplorerPage", "collections.CategoryPage"]
    subpage_types = ["collections.CategoryPage", "collections.ResultsPage"]


class ResultsPage(Page):
    """Results page.

    This page is a placeholder for the results page at the end of a user's
    journey through the collection explorer.

    Eventually, this page will run an editor-defined query against the
    collections API and display the results.
    """

    max_count_per_parent = 1
    parent_page_types = ["collections.CategoryPage"]
    subpage_types = []
