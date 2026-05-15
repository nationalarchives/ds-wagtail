from app.core.blocks.image import APIImageChooserBlock
from app.core.blocks.paragraph import APIRichTextBlock
from app.core.blocks.promoted_links import FeaturedExternalLinkBlock, FeaturedPageBlock
from app.core.blocks.video import YouTubeBlock
from app.media.blocks import MediaBlock
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail import blocks


# Resources
class QuestionBlock(blocks.StreamBlock):
    question = blocks.StructBlock(
        [
            (
                "question_heading",
                blocks.CharBlock(
                    required=False,
                    max_length=255,
                ),
            ),
            (
                "guidance_for_teachers",
                APIRichTextBlock(
                    features=["bold", "italic", "link", "ul"],
                    required=False,
                ),
            ),
        ],
        icon="help",
    )


class SourceImageWithCaptionBlock(blocks.StructBlock):
    image = APIImageChooserBlock(
        rendition_size="max-900x900",
        help_text="An image for the source.",
    )
    caption = APIRichTextBlock(features=["bold", "italic"], required=False)


class SourceMediaWithCaptionBlock(MediaBlock):
    title = None
    caption = APIRichTextBlock(features=["bold", "italic"], required=False)


class SourceYouTubeWithCaptionBlock(MediaBlock):
    youtube = YouTubeBlock()
    caption = APIRichTextBlock(features=["bold", "italic"], required=False)


class SourceMediaBlock(blocks.StreamBlock):
    image = SourceImageWithCaptionBlock()
    video = SourceMediaWithCaptionBlock()
    youtube = SourceYouTubeWithCaptionBlock()

    class Meta:
        label = "Source media"


class SourceFeaturedLinkBlock(blocks.StreamBlock):
    external_link = FeaturedExternalLinkBlock()
    internal_link = FeaturedPageBlock()

    class Meta:
        label = "Source featured link"


# Sessions
class VenueDetailsBlock(blocks.StructBlock):
    venue_name = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Venue name"),
        help_text=_("Required only when location type is Custom venue."),
    )

    class SessionRegions(models.TextChoices):
        SOUTH_EAST_LONDON = "south_east_london", "South East and London"
        SOUTH_WEST = "south_west", "South West"
        MIDLANDS = "midlands", "Midlands"
        NORTH_EAST = "north_east", "North East"
        NORTH_WEST = "north_west", "North West"

    session_regions = blocks.ChoiceBlock(
        choices=SessionRegions.choices,
        label=_("Regions"),
        help_text=_("The regions where the session is offered."),
        required=False,
    )

    address_line_1 = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Address line 1"),
    )
    address_line_2 = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Address line 2"),
    )
    postcode = blocks.CharBlock(
        required=False,
        max_length=20,
        label=_("Postcode"),
    )

    class Meta:
        icon = "home"
        label = _("Additional venue details")
        classname = "collapsed"
