from app.core.blocks.image import (
    APIImageChooserBlock,
    ImageGalleryBlock,
    PartnerLogoChooserBlock,
)
from app.core.blocks.page_chooser import APIPageChooserBlock
from app.core.blocks.paragraph import APIRichTextBlock
from app.core.blocks.promoted_links import FeaturedExternalLinkBlock, FeaturedPageBlock
from app.core.blocks.quote import QuoteBlock
from app.core.blocks.section import SubHeadingBlock
from app.core.blocks.video import YouTubeBlock
from app.core.models import (
    BasePageWithRequiredIntro,
    PublishedDateMixin,
    RequiredHeroImageMixin,
)
from app.core.serializers import RichTextSerializer
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable

from ..blocks import (
    QuestionBlock,
    SourceMediaBlock,
)
from ..serializers import (
    KeyStageSerializer,
    SourceSerializer,
    ThemeSerializer,
    TimePeriodSerializer,
)

# TODO: sort panel order on promote tabs


class KeyStage(models.Model):
    """A model for individual key stage tags - choices are populated by migrations/0002_seed_key_stages.py"""

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
        unique=True,
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
        verbose_name = _("Time period")
        verbose_name_plural = _("Time periods")

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
        verbose_name = _("Theme")
        verbose_name_plural = _("Themes")

    def __str__(self):
        return self.name


class Source(Orderable):
    page = ParentalKey(
        "education.TeachingResourcePage",
        on_delete=models.CASCADE,
        related_name="sources",
    )

    source_title = models.CharField(
        verbose_name=_("source title"),
        help_text=_("A unique, descriptive title for the source."),
        blank=True,
        max_length=160,
    )

    # Source Media
    source_image = StreamField(
        [
            (
                "source_image",
                APIImageChooserBlock(
                    rendition_size="max-900x900",
                    verbose_name=_("source image"),
                    help_text=_("An image for the source."),
                    blank=True,
                ),
            )
        ],
    )

    source_media = StreamField(
        [
            (
                "source_media",
                SourceMediaBlock(
                    verbose_name=_("source media"),
                    help_text=_("A piece of media for the source."),
                    blank=True,
                ),
            )
        ],
    )

    source_youtube = StreamField(
        [
            (
                "source_youtube",
                YouTubeBlock(
                    verbose_name=_("source youtube video"),
                    help_text=_("A youtube video for the source."),
                    blank=True,
                ),
            )
        ],
    )

    source_media_caption = StreamField(
        [("source_media_caption", APIRichTextBlock(features=["bold", "italic"]))],
        verbose_name=_("source caption"),
        help_text=_("If provided, displays directly below the source."),
        blank=True,
        null=True,
    )

    # Source link
    source_media_featured_link = StreamField(
        [
            (
                "source_media_featured_link",
                APIPageChooserBlock(
                    label="Internal page",
                    required=False,
                    page_type="wagtailcore.Page",
                ),
            )
        ],
        verbose_name=_("source media featured link"),
        help_text=_("Reference another page published on the site"),
        blank=True,
        max_num=1,
    )

    source_media_featured_external_link = models.URLField(
        verbose_name=_("source media featured link"),
        help_text=_(
            "Option to add link to a resource on a 3rd party platform (e.g. mapping tool)"
        ),
        blank=True,
    )

    # Source description
    source_description = StreamField(
        [
            (
                "source_description",
                APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"]),
            )
        ],
        verbose_name=_("source description"),
        help_text=_(
            "An optional free text field to add in a fuller description of the source."
        ),
        blank=True,
        null=True,
    )

    # Source questions
    source_question = StreamField(
        QuestionBlock(
            verbose_name=("source question"),
            help_text=("A series of questions relating to each source."),
        ),
        blank=True,
    )

    panels = [
        FieldPanel("source_title"),
        FieldPanel("source_image"),
        FieldPanel("source_media"),
        FieldPanel("source_youtube"),
        FieldPanel("source_media_caption"),
        FieldPanel("source_media_featured_link"),
        FieldPanel("source_media_featured_external_link"),
        FieldPanel("source_description"),
        FieldPanel("source_question"),
    ]


class CurriculumConnection(Orderable):
    page = ParentalKey(
        "education.TeachingResourcePage",
        on_delete=models.CASCADE,
        related_name="curriculum_connections",
    )

    key_stage = models.ForeignKey(
        "education.KeyStage",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Key stage"),
        help_text=_("The key stage for this curriculum connection."),
    )

    curriculum_connection_description = RichTextField(
        features=["bold", "italic", "link", "ul"],
        verbose_name=_("curriculum connection description"),
        help_text=_("Add the curriculum connection description."),
        blank=True,
        null=True,
    )

    panels = [
        FieldPanel("key_stage"),
        FieldPanel("curriculum_connection_description"),
    ]


class TeachingResourcePage(
    PublishedDateMixin, RequiredHeroImageMixin, BasePageWithRequiredIntro
):
    """A page to display a teaching resource"""

    parent_page_types = [
        "education.TeachingResourcesListingPage",
    ]

    enquiry_question = models.CharField(
        verbose_name=_("enquiry question"),
        blank=True,
        max_length=160,
    )

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

    # Body
    sources_title = models.CharField(
        verbose_name=_("sources title"),
        help_text=_(
            "Title of the main section of the page. In most cases ‘Investigate the sources’"
        ),
        blank=True,
        max_length=160,
    )

    sources_introduction = RichTextField(
        features=["bold", "italic", "link"],
        verbose_name=_("sources introduction"),
        help_text=_("Optional text field to provide an introduction to the sources."),
        blank=True,
        null=True,
    )

    # Teacher’s Notes*
    teachers_notes = RichTextField(
        features=["bold", "italic", "link", "ol", "ul"],
        verbose_name=_("teachers notes"),
        help_text=_(
            "A general overview of what the resource contains and how it can be used."
        ),
        blank=True,
        null=True,
    )

    # Extension activities
    extension_activities = StreamField(
        [
            (
                "paragraph",
                APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"]),
            ),
            ("sub_heading", SubHeadingBlock()),
            ("featured_page", FeaturedPageBlock()),
            ("featured_external_link", FeaturedExternalLinkBlock()),
        ],
        verbose_name=_("extension activities"),
        help_text=_(
            "Optional section where editors can add extra activities for teachers to try with their pupils."
        ),
        blank=True,
        null=True,
    )

    # Background information
    background_information = StreamField(
        [
            (
                "paragraph",
                APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"]),
            ),
            ("sub_heading", SubHeadingBlock()),
        ],
        verbose_name=_("background information"),
        help_text=_("Section providing historical context to the teaching resource."),
        blank=True,
        null=True,
    )

    # Further information
    further_information_title = models.CharField(
        max_length=255,
        verbose_name=_("further information title"),
        help_text=_("Title of the further information section."),
        blank=True,
        null=True,
    )

    further_information = StreamField(
        [
            (
                "paragraph",
                APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"]),
            ),
            ("sub_heading", SubHeadingBlock()),
            ("featured_external_link", FeaturedExternalLinkBlock()),
            ("featured_page", FeaturedPageBlock()),
        ],
        verbose_name=_("further information"),
        help_text=_("Section providing links to other useful information."),
        blank=True,
        null=True,
    )

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            FieldPanel("enquiry_question"),
            MultiFieldPanel(
                [
                    FieldPanel("sources_title"),
                    FieldPanel("sources_introduction"),
                    InlinePanel(
                        "sources",
                        label=_("Source"),
                        heading=_("Sources"),
                        min_num=1,
                    ),
                ],
                heading=_("Sources"),
            ),
            FieldPanel("teachers_notes"),
            InlinePanel(
                "curriculum_connections",
                label=_("Curriculum connection"),
                heading=_("Connections to the curriculum"),
                min_num=1,
            ),
            FieldPanel("extension_activities"),
            FieldPanel("background_information"),
            MultiFieldPanel(
                [
                    FieldPanel("further_information_title"),
                    FieldPanel("further_information"),
                ],
                heading=_("Further information"),
            ),
        ]
    )

    promote_panels = (
        BasePageWithRequiredIntro.promote_panels
        + PublishedDateMixin.promote_panels
        + [
            FieldPanel("key_stage"),
            FieldPanel("time_period"),
            FieldPanel("theme"),
        ]
    )

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("hero_image"),
        APIField("enquiry_question"),
        APIField("key_stage", serializer=KeyStageSerializer()),
        APIField("time_period", serializer=TimePeriodSerializer()),
        APIField("theme", serializer=ThemeSerializer()),
        APIField("sources_title"),
        APIField("sources_introduction", serializer=RichTextSerializer()),
        APIField("teachers_notes"),
        APIField("sources", serializer=SourceSerializer(many=True)),
        APIField("curriculum_connection_description", serializer=RichTextSerializer()),
        APIField("extension_activities"),
        APIField("background_information"),
        APIField("further_information_title"),
        APIField("further_information"),
    ]


# TODO: make this more generic? This is lifted from EducationReadMoreLink just as PoC and I don't like that
class RelatedEducationSessions(Orderable):
    """Links to take users to related educaiton sessions"""

    page = ParentalKey(
        "education.EducationSessionPage",
        on_delete=models.CASCADE,
        related_name="related_education_sessions",
    )

    selected_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("selected page"),
        help_text=_("Navigation to other Education sessions"),
    )

    panels = [
        PageChooserPanel("selected_page"),
    ]

    class Meta:
        verbose_name = _("related education session")
        ordering = ["sort_order"]


class EducationSessionPage(
    PublishedDateMixin, RequiredHeroImageMixin, BasePageWithRequiredIntro
):
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

    # Page title* - default

    # Hero image* - mixin

    # Introductory text* -  mixin

    # Rich text formatting (bold, italics, links)

    # Start date  and End date
    # hlep taxt placeholder, should be put at start of panel if so

    start_date = models.DateField(
        verbose_name=_("start date"),
        null=True,
        editable=False,
        help_text=_(
            "If neither start nor end date is added this will default to 'All Year'"
        ),
    )

    end_date = models.DateField(
        verbose_name=_("end date"),
        null=True,
        editable=False,
        help_text=_(
            "If neither start nor end date is added this will default to 'All Year'"
        ),
    )

    # Optional field - Not all sessions have a specific date/dates

    # TODO: Default to ‘All year' if no start and end date is added.
    # [tick box? date optional?]

    # or

    # pick a start and end date from a date picker.

    # startDate - Schema.org Property

    # endDate - Schema.org Property

    # TODO:
    # Key stage

    # Pull from metadata

    # snippets? hard coded? models?

    # Time period

    # Pull from metadata

    # Theme

    # Pull from metadata

    # --------Event key details bar

    # Session price*

    # Whether the session is free or paid (note, most are free)

    # Default to ‘Free to UK schools’ if no text added

    # Price field (optional)
    # Price detail (plain text) (optional - not without price)

    # price - Schema.org Property

    session_price = None  # Optional float

    # TOFO:Add validation
    # or is this just a preferred currency format
    session_price_detail = models.CharField(  # TODO- conditionally required,
        verbose_name=_("session price detail"),
        help_text=_("An explanation of the price."),
        blank=True,
        max_length=160,
    )

    # Location*

    session_location = None
    # write migration to seed choices? Maybe not, these could change a lot given recent talks?

    # Ability to add one or more locations to the session

    # Note, duration of sessions can vary depending on location, so duration info is added with each location info

    # e.g.

    # Online

    # The National Archives

    # Your school

    # The Discovery Museum
    # Blandford Square, Newcastle upon Tyne, NE1 4JA

    # Museum of Richmond
    # 2nd Floor, Old Town Hall, Whittaker Avenue, Richmond, TW9 1TP.

    # Select from:
    # - Online’
    # - ‘At the National Archives'
    # - At your school

    # OR:

    # Venue name [free text]
    # Venue address [optional
    # First line
    # Second line
    # postcode]

    # Duration [free text}

    session_location_duration = models.CharField(
        verbose_name=_("session duration"),
        help_text=_("A clear description of the session duration."),
        blank=True,
        max_length=160,
    )

    # Region
    # [Regions:
    # South East and London
    # South West
    # Midlands
    # North East
    # North West ]

    session_regions = None

    # PostalAddress - Schema.org Type (postalCode)
    session_postal_address = None
    # Recommended for*

    # Key stage link

    # Pull from Key Stage metadata
    session_reccomended_for = None  # required

    # Duration

    # How long each session is. This will vary depending on location so will pull info from the location info above.

    # Shows in front end in format of:

    # At [venue name] – [duration]

    # e.g. Online – 1 hour

    # At The National Archives – 2 hours

    # At The Discovery Museum – 1 hour

    # At your school – 1 to 2 hours

    # Location text:
    # either ‘online’ 'At the National Archives, or Venue Name from location info

    # Duration text: duration from location info (see above)

    session_duration = None

    # Booking link

    # Link to book tickets. In most cases the same Eventbrite link, but some will have their own specific link

    session_booking_link = models.URLField(
        null=True,
        blank=True,
        help_text="Link to booking page",
        verbose_name="Booking link",
    )

    # On front end, text will say ‘Book now’

    # Add link

    # ----------Event section

    # Event body
    # Field name

    # Event description*

    # Main body of the page where the session and what to expect from it are described

    # - Paragraph text
    session_description = RichTextField(
        features=["bold", "italic", "link", "ul"],
        verbose_name=_("session description"),
        help_text=_("Add the session description."),
        blank=True,
        null=True,
    )
    # - Heading
    session_title = models.CharField(
        verbose_name=_("session title"),
        help_text=_("A unique, descriptive title for the session."),
        blank=True,
        max_length=160,
    )
    # - Partner logo

    partner_logo = StreamField(
        [
            (
                "partner_logo",
                PartnerLogoChooserBlock(
                    rendition_size="max-900x900",
                    verbose_name=_("partner logo"),
                    help_text=_("An image for the partner logo."),
                    blank=True,
                ),
            )
        ],
    )
    # - Quote
    session_quote = StreamField(
        [
            (
                "session_quote",
                QuoteBlock(
                    help_text=_("A quote with an attribution related to the session."),
                    blank=True,
                    null=True,
                ),
            )
        ],
    )
    # - Inset text TODO: clarify this for better naming but for now
    inset_text = RichTextField(
        features=["bold", "italic", "link", "ul"],
        verbose_name=_("inset text"),
        help_text=_(
            "Inset text - TODO ask for better decsription of this? where it sits etc"
        ),
        blank=True,
        null=True,
    )

    # Connections to the curriculum - not the same as in resources? but assuming they're repeatable?

    # Area headed ‘Connection to the curriculum' (title hard coded) where specific connections to the curriculum can be listed. Note these is more specific connections than the themes (e.g. might specify exam board), so is a free text area.

    # Rich text - Italic, bold, bulleted lists, numbered lists, links
    curriculum_connection_description = StreamField(
        [
            (
                "curriculum_connection_description",
                APIRichTextBlock(features=["bold", "italic", "link", "ol", "ul"]),
            )
        ],
        verbose_name=_("source description"),
        help_text=_(
            "An optional free text field to add in a fuller description of the source."
        ),
        blank=True,
        null=True,
    )

    # Event highlights
    # Nice to have. Not for MVP - easy to add though

    # Same as Event highlights component

    session_highlights = StreamField(
        [("session_highlights", ImageGalleryBlock())],
        blank=True,
        help_text=_("Optional image gallery to show what to expect from the session."),
        max_num=1,
    )

    # Contact us - contact us component?

    # Area where users can find out where to get support with their booking

    # Will be the same in most cases but some will have different contact info.

    # Make them fill it in every time. Copy the Contact us component

    # Text

    # email

    # phone number

    # Newsletter to be handled in the frontend

    # More education sessions  - handled by frontend? use cached property to get them from taxonomies?
    # then allow override using the selected pages from related_education_sessions via RelatedEducationSessions

    # TODO: think about adding key details tab ala /services/ds-wagtail/app/whatson/models/details.py: for key details bar lol

    #     edit_handler = TabbedInterface(
    #         [
    #             ObjectList(content_panels, heading="Content"),
    #             ObjectList(key_details_panels, heading="Key details"),
    #             ObjectList(promote_panels, heading="Promote"),
    #             ObjectList(BasePageWithRequiredIntro.settings_panels, heading="Settings"),
    #         ]
    #     )

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            FieldPanel("start_date"),  # TODO: default to all year
            FieldPanel("end_date"),
            MultiFieldPanel(
                [
                    MultiFieldPanel(
                        [
                            # FieldPanel("session_price"), #make this multifield panel?
                            MultiFieldPanel(
                                [
                                    FieldPanel("session_price"),
                                    FieldPanel("session_price_detail"),
                                ],
                                heading=_("Session price"),
                            ),
                            MultiFieldPanel(
                                [  # TODO: sort this out - location and duration linked
                                    # does this need to be multifield? probs not look at spec to double chec no other firleds
                                    InlinePanel("session_location"),
                                    FieldPanel("session_location_duration"),
                                ],
                                heading=_("Session location"),
                            ),
                            FieldPanel("session_regions"),
                            FieldPanel("session_postal_address"),
                            # FieldPanel("session_reccomended_for"),
                            # FieldPanel("session_duration"),
                            FieldPanel("session_booking_link"),
                        ],
                        heading=_("Session description"),
                    ),
                    # FieldPanel("curriculum_connection_description"),
                    # FieldPanel("session_highlights"),
                ],
                heading=_("Session key details bar"),
            ),
            MultiFieldPanel(
                [
                    MultiFieldPanel(
                        [
                            FieldPanel("session_description"),
                            FieldPanel("session_title"),
                            FieldPanel("partner_logo"),
                            FieldPanel("session_quote"),
                            FieldPanel("inset_text"),
                        ],
                        heading=_("Session description"),
                    ),
                    FieldPanel("curriculum_connection_description"),
                    FieldPanel("session_highlights"),
                ]
            ),
            FieldPanel("key_stage"),
            FieldPanel("time_period"),
            FieldPanel("theme"),
            InlinePanel(
                "related_education_sessions",
                heading=_("More education sessions"),
                help_text=_(
                    "Education sessions that are selected to be shown in the related education sesisons section"
                ),
            ),
        ]
    )

    promote_panels = (
        BasePageWithRequiredIntro.promote_panels
        + PublishedDateMixin.promote_panels
        + [
            FieldPanel("key_stage"),
            FieldPanel("time_period"),
            FieldPanel("theme"),
        ]
    )

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("key_stage", serializer=KeyStageSerializer()),
        APIField("time_period", serializer=TimePeriodSerializer()),
        APIField("theme", serializer=ThemeSerializer()),
    ]
