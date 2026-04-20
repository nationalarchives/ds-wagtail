from app.core.models import (
    BasePageWithRequiredIntro,
)
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    InlinePanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.models import Orderable


class EducationPage(BasePageWithRequiredIntro):
    """
    A page for listing teaching resources and sessions.
    """

  
    # featured_teaching_resource = models.ForeignKey(  
    #     "education.EducationResourcePage",  
    #     null=True,  
    #     blank=True,  
    #     on_delete=models.SET_NULL,  
    #     related_name="+",  
    #     verbose_name=_("featured teaching resource"),  
    #     help_text=_("Option to add a highlighted teaching resource, particularly for history months etc"),  
    # )


    # featured_education_session = models.ForeignKey(  
    #     "education.EducationSessionPage",  
    #     null=True,  
    #     blank=True,  
    #     on_delete=models.SET_NULL,  
    #     related_name="+",  
    #     verbose_name=_("featured education session"),  
    #     help_text=_("Page picker to highlight a featured education session"),  
    # )  

    @cached_property
    def type_label(cls) -> str:
        return "Education"

    class Meta:
        verbose_name = _("Education landing page")

    parent_page_types = [
        "home.HomePage",
    ]

    subpage_types = [
        "education.EducationSessionsListingPage",
        "education.EducationResourcesListingPage",
    ]

    max_count = 1

    content_panels = BasePageWithRequiredIntro.content_panels + [
        InlinePanel(
            "education_page_selections",
            heading=_("Page selections"),
            help_text=_("Select pages to display on the Education page."),
        ),
    ]

class EducationPageSelection(Orderable):
    """
    This model is used to select a page to display on the Education page.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="education_page_selections",
    )

    selected_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("selected page"),
        help_text=_("The page to display on the Education page."),
    )

#TODO: figure out what panels are needed
    panels = [
        PageChooserPanel(
            "selected_page",
            page_type=[
                "education.EducationResourcesListingPage",
                "education.EducationSessionsListingPage",
            ],
        ),
    ]

    class Meta:
        verbose_name = _("selection")
        ordering = ["sort_order"]



