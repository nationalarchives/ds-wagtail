from app.core.blocks.image import (
    ImageGalleryBlock,
    PartnerLogoChooserBlock,
)
from app.core.blocks.paragraph import APIRichTextBlock
from app.core.blocks.quote import QuoteBlock
from app.core.models import (
    BasePageWithRequiredIntro,
    PublishedDateMixin,
    RequiredHeroImageMixin,
)
from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
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

from ..serializers import (
    KeyStageSerializer,
    ThemeSerializer,
    TimePeriodSerializer,
)
from .details import (
    BaseKeyStageTag,
    BaseThemeTag,
    BaseTimePeriodTag,
)

# TODO: sort panel order on promote tabs


class EducationSessionPageKeyStageTag(BaseKeyStageTag):
    page = ParentalKey(
        "education.EducationSessionPage",
        on_delete=models.CASCADE,
        related_name="education_keystage_tags",
    )


class EducationSessionPageTimePeriodTag(BaseTimePeriodTag):
    page = ParentalKey(
        "education.EducationSessionPage",
        on_delete=models.CASCADE,
        related_name="education_time_period_tags",
    )


class EducationSessionPageThemeTag(BaseThemeTag):
    page = ParentalKey(
        "education.EducationSessionPage",
        on_delete=models.CASCADE,
        related_name="education_theme_tags",
    )


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

    @cached_property
    def key_stages(self):
        return [
            tag.key_stage
            for tag in self.education_keystage_tags.select_related("key_stage")
        ]

    @cached_property
    def time_periods(self):
        return [
            tag.time_period
            for tag in self.education_time_period_tags.select_related("time_period")
        ]

    @cached_property
    def themes(self):
        return [tag.theme for tag in self.education_theme_tags.select_related("theme")]

    @cached_property
    def key_stage(self):
        return self.key_stages[0] if self.key_stages else None

    @cached_property
    def time_period(self):
        return self.time_periods[0] if self.time_periods else None

    @cached_property
    def theme(self):
        return self.themes[0] if self.themes else None

    # Page title* - default

    # Hero image* - mixin

    # Introductory text* -  mixin

    # Rich text formatting (bold, italics, links)

    # Start date  and End date
    # hlep taxt placeholder, should be put at start of panel if so

    session_start_date = models.DateField(
        verbose_name=_("start date"),
        null=True,
        help_text=_(
            "If neither start nor end date is added this will default to 'All Year'"
        ),
    )

    session_end_date = models.DateField(
        verbose_name=_("end date"),
        null=True,
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
                ),
            )
        ],
        blank=True,
    )
    # - Quote
    session_quote = StreamField(
        [
            (
                "session_quote",
                QuoteBlock(
                    help_text=_("A quote with an attribution related to the session."),
                ),
            )
        ],
        blank=True,
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
    session_curriculum_connection_description = StreamField(
        [
            (
                "session_curriculum_connection_description",
                APIRichTextBlock(features=settings.RESTRICTED_RICH_TEXT_FEATURES),
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
            FieldPanel("session_start_date"),  # TODO: default to all year
            FieldPanel("session_end_date"),
            MultiFieldPanel(
                [
                    MultiFieldPanel(
                        [
                            # FieldPanel("session_price"), #make this multifield panel?
                            MultiFieldPanel(
                                [
                                    FieldPanel("session_price_detail"),
                                ],
                                heading=_("Session price"),
                            ),
                            MultiFieldPanel(
                                [  # TODO: sort this out - location and duration linked
                                    # does this need to be multifield? probs not look at spec to double chec no other firleds
                                    FieldPanel("session_location_duration"),
                                ],
                                heading=_("Session location"),
                            ),
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
                    FieldPanel("session_curriculum_connection_description"),
                    FieldPanel("session_highlights"),
                ]
            ),
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
            InlinePanel(
                "education_keystage_tags",
                label=_("Key stage"),
                heading=_("Key stages"),
            ),
            InlinePanel(
                "education_time_period_tags",
                label=_("Time period"),
                heading=_("Time periods"),
            ),
            InlinePanel(
                "education_theme_tags",
                label=_("Theme"),
                heading=_("Themes"),
            ),
        ]
    )

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("key_stage", serializer=KeyStageSerializer()),
        APIField("time_period", serializer=TimePeriodSerializer()),
        APIField("theme", serializer=ThemeSerializer()),
        APIField("key_stages", serializer=KeyStageSerializer(many=True)),
        APIField("time_periods", serializer=TimePeriodSerializer(many=True)),
        APIField("themes", serializer=ThemeSerializer(many=True)),
    ]
