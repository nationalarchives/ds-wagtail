from app.core.models import BasePageWithIntro
from django.db import models
from wagtail.models import Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey


class AccessIndexPage(BasePageWithIntro):
    """
    A page that provides information about access to the National Archives.
    """

    @property
    def access_points(self):
        """
        Returns a list of access points for the National Archives.
        """
        return self.get_children().live().public().specific()
    

    subpage_types = [
        "access.AccessLandingPage",
    ]

    parent_page_types = [
        "home.HomePage",
    ]

    max_count = 1

class AccessListing(Orderable):
    """
    An orderable model that represents a listing of access points for the National Archives.
    """

    page = ParentalKey(
        "access.AccessLandingPage",
        on_delete=models.CASCADE,
        related_name="access_listings",
    )
    access_point = models.ForeignKey(
        "access.AccessPage",
        on_delete=models.CASCADE,
        related_name="+",
    )

class AccessLandingPage(BasePageWithIntro):
    """
    A landing page for access-related content.
    """

    content_panels = BasePageWithIntro.content_panels + [
        InlinePanel("access_listings"),
    ]

    subpage_types = [
        "access.AccessPage",
    ]

    parent_page_types = [
        "access.AccessIndexPage",
    ]

class AccessPage(BasePageWithIntro):
    """
    A page that provides detailed information about access to the National Archives.
    """
    subpage_types = []

    parent_page_types = [
        "access.AccessLandingPage",
    ]