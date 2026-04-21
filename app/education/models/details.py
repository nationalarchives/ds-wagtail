from app.core.models import (
    BasePageWithRequiredIntro,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.models import Orderable
from wagtail.fields import RichTextField

from ..serializers import KeyStageSerializer, ThemeSerializer, TimePeriodSerializer




# Key stage

# Relevant key stage for the resource. Shows on page and also drives filters and search

# Multi select. 

# Taken from set taxonomy

# MVP Education Taxonomy
 

 

 

# Time period

# Primary Time period

# Secondary time periods

# Relevant time periods for the resource. Shows on page and also drives filters and search

# Taken from set taxonomy

# MVP Education Taxonomy
 

# Can only select one primary time period

# Can select multiple secondary time periods

 

 

# Theme

# Primary Theme

# Secondary Theme

# Relevant themes for the resource. Shows on page and also drives filters and search

# Taken from set taxonomy

# MVP Education Taxonomy
 

# Can only select one primary theme

# Can select multiple secondary theme


class KeyStageTag(Orderable):
    """
    This model is used to tag Education pages.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="page_key_stage_tags",
    )

    key_stage = models.ForeignKey(
        "education.KeyStage",
        on_delete=models.CASCADE,
        related_name="key_stage",
        verbose_name=_("Key stage"),
        help_text=_("The key stage of the page."),
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = _("Key stage")
        verbose_name_plural = _("Key stages")

    def __str__(self):
        return f"{self.page.title}: {self.key_stage.name}"


class KeyStage(models.Model):
    """A model for key stage tags"""

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
        unique=True,
    )

    class Meta:
        verbose_name = _("Key stage")
        verbose_name_plural = _("Key stages")

    def __str__(self):
        return self.name


class TimePeriod(models.Model):
    """A model for time period tags"""

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
        unique=True,
    )

    class Meta:
        verbose_name = _("Key stage")
        verbose_name_plural = _("Key stages")

    def __str__(self):
        return self.name


class Theme(models.Model):
    """A model for theme tags"""

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
        unique=True,
    )

    class Meta:
        verbose_name = _("Key stage")
        verbose_name_plural = _("Key stages")

    def __str__(self):
        return self.name


class TeachingResourcePage(BasePageWithRequiredIntro):
    """A page to display a teaching resource"""

    parent_page_types = [
        "education.TeachingResourcesListingPage",
    ]

# Hero 

# TODO: Hero image

# TODO: Enquiry question


    key_stage = models.ForeignKey(
        "education.KeyStage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("key stage"),
    )

    time_period = models.ForeignKey(
        "education.TimePeriod",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("time period"),
    )

    theme = models.ForeignKey(
        "education.Theme",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("theme"),
    )

#Body

#TODO ensure this is the right way to do this
# H2
# Plain text

    sources_title = models.TextField(
        verbose_name=_("sources title"),
        help_text=_(
            "Title of the main section of the page. In most cases ‘Investigate the sources’"
        ),
        blank=True,
    )

     sources_introduction = RichTextField(
        verbose_name=_("sources introduction"),
        help_text=_(
            "Optional text field to provide an introduction to the sources." 
        ),
        blank=True,
    )

 

# TODO Source* do as inline panels so multiple can be added 

# A document or piece of media for the students to use. In most cases this will be an image or number of images, it may also be a piece of audio, a video or an external link to a resource hosted on a 3rd party platform. 

# Ability to add multiple sources to the page. Mandatory to have at least one. 

 

 

# Source title*

# A unique, descriptive title for the source

     source_title = models.TextField(
        verbose_name=_("sources title"),
        help_text=_(
            "A unique, descriptive title for the source."
        ),
        blank=True,
    )


 

# Source media TODO

     source_image = models.TextField(
        verbose_name=_("sources title"),
        help_text=_(
            "A unique, descriptive title for the source."
        ),
        blank=True,
    )

     source_media = models.TextField(
        verbose_name=_("sources title"),
        help_text=_(
            "A unique, descriptive title for the source."
        ),
        blank=True,
    )

     source_youtube = models.TextField(
        verbose_name=_("sources title"),
        help_text=_(
            "A unique, descriptive title for the source."
        ),
        blank=True,
    )

# Editor picks the media associated with the source. 

# Can pick Image, Media, YouTube video. 

# Multi select allowed

# Media will inherit and show on the page all relevant metadata e.g. transcript, translation, alt text, copyright

# Note - How to show if an image has an audio transcript?

 

 

# Media caption

# Option to add a caption to the source e.g. Catalogue reference. 

# Note, if image has copyright metadata, this will show in the  caption field.  

# Rich text - allow bold, italic

      source_media_caption = RichTextField(
        verbose_name=_("sources title"),
        help_text=_(
            "Option to add a caption to the source e.g. Catalogue reference."
        ),
        blank=True,
    )

 

# Source link

# Option to add link to a resource on a 3rd party platform (e.g. mapping tool)

# Featured external link

# Featured link

       source_media_link = RichTextField(
        verbose_name=_("sources title"),
        help_text=_(
            "Option to add a caption to the source e.g. Catalogue reference."
        ),
        blank=True,
    )


 

# Source description

# An optional free text field to add in a fuller description of the source.

# Rich text - allow bold, italic, hyperlinks, bullets, numbered lists

 

 

# Source questions

# A series of questions relating to each source. 

# Note: Guidance from TBX, suggests a taxonomy for the question headings, but for ease of migration, use free text Subheadings. 

# Paragraph text (rich text - Bold, Italics, Bulleted list, hyperlink)

# Subheadings

 

 

 



# Teacher’s Notes*

# Free text field giving a general overview of what the resource contains and how it can be used.  

# Rich text -  allow bold, italic, hyperlinks, bullets, numbered lists

 

 

# Connections to the curriculum*

# Area where editors can add a list of links to the curriculum, structured by Key stage

# Multi add connections:

# Key stage (select from Key stage taxonomy)

# Connection description  - Rich text field (bold, italic, hyperlink, bulleted list)

 

 

 

 

 

# Extension activities

# Optional section where editors can add in extra activities for teachers to try with their pupils

# Paragraph text 

# Subheadings

# Featured page

# Featured external link

 

 

# Background information

# Section providing historical context to the teaching resource

# Paragraph text

# Subheadings

 

 

# Further information

# Section providing links to other useful information. 
# Title of section free text rather than hard coded to give editor flexibility

# Title* 

# Paragraph text 

# Subheadings

# Featured external links

# Featured page



    content_panels = BasePageWithRequiredIntro.content_panels + [
        MultiFieldPanel(
            [
                PageChooserPanel("featured_teaching_resource"),
                FieldPanel("featured_teaching_resource_teaser_override"),
            ],
            heading=_("Sources"),
        ),
        MultiFieldPanel(
            [
                PageChooserPanel("featured_teaching_resource"),
                FieldPanel("featured_teaching_resource_teaser_override"),
            ],
            heading=_("Teacher's notes"),
        ),
        MultiFieldPanel(
            [
                PageChooserPanel("featured_teaching_resource"),
                FieldPanel("featured_teaching_resource_teaser_override"),
            ],
            heading=_("Extension activities"),
        ),
        MultiFieldPanel(
            [
                PageChooserPanel("featured_teaching_resource"),
                FieldPanel("featured_teaching_resource_teaser_override"),
            ],
            heading=_("Background information"),
        ),
        MultiFieldPanel(
            [
                PageChooserPanel("featured_teaching_resource"),
                FieldPanel("featured_teaching_resource_teaser_override"),
            ],
            heading=_("Further reading"),
        ),
    ]


    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("key_stage", serializer=KeyStageSerializer()),
        APIField("time_period", serializer=TimePeriodSerializer()),
        APIField("theme", serializer=ThemeSerializer()),
    ]

 

 
# META TAB
# Short title

 
# Internal data 

# Teaser text*

# Teaser image



class EducationSessionPage(BasePageWithRequiredIntro):
    """A page to display an education session"""

    parent_page_types = [
        "education.EducationSessionsListingPage",
    ]

    key_stage = models.ForeignKey(
        "education.KeyStage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("key stage"),
    )

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("key_stage", serializer=KeyStageSerializer()),
    ]


class EducationReadMoreLink(Orderable):
    """Navigation links for the Read more section"""

    page = ParentalKey(
        "education.EducationPage",
        on_delete=models.CASCADE,
        related_name="education_read_more_links",
    )

    selected_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("selected page"),
        help_text=_("Navigation to other sections within Education"),
    )

    panels = [
        PageChooserPanel("selected_page"),
    ]

    class Meta:
        verbose_name = _("read more link")
        ordering = ["sort_order"]
