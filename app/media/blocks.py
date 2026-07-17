from django.core.exceptions import ValidationError
from wagtail import blocks
from wagtail.rich_text import expand_db_html
from wagtailmedia.blocks import AbstractMediaChooserBlock

from app.core.blocks.image import APIImageChooserBlock
from app.media.time_utils import format_seconds_hhmmss, parse_chapter_time_to_seconds

CHAPTER_TIME_VALIDATION_MESSAGE = (
    "The accepted format is HH:MM:SS, minutes and seconds must be between 00 and 59."
)


def chapter_time_validation_error(value):
    return ValidationError(f"{CHAPTER_TIME_VALIDATION_MESSAGE} You wrote: {value!r}.")


def normalise_chapter_time_for_display(value):
    if value in (None, ""):
        return value

    if isinstance(value, int):
        return format_seconds_hhmmss(value)

    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            return format_seconds_hhmmss(int(stripped))

        parts = stripped.split(":")
        if len(parts) == 3 and all(part.isdigit() for part in parts):
            hours, minutes, seconds = map(int, parts)
            if hours >= 0 and 0 <= minutes <= 59 and 0 <= seconds <= 59:
                total_seconds = hours * 3600 + minutes * 60 + seconds
                return format_seconds_hhmmss(total_seconds)

    return value


class ChapterTimeBlock(blocks.CharBlock):
    def clean(self, value):
        data = super().clean(value)
        if data in (None, ""):
            return data

        try:
            hours, minutes, seconds = (int(part) for part in data.split(":", 2))
        except ValueError:
            raise chapter_time_validation_error(data)

        if hours < 0 or not (0 <= minutes <= 59 and 0 <= seconds <= 59):
            raise chapter_time_validation_error(data)

        return data

    def to_python(self, value):
        return super().to_python(normalise_chapter_time_for_display(value))

    def get_prep_value(self, value):
        prepped_value = super().get_prep_value(value)
        return parse_chapter_time_to_seconds(prepped_value)

    def get_form_state(self, value):
        return super().get_form_state(normalise_chapter_time_for_display(value))


class MediaChooserBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        """
        AbstractMediaChooserBlock requires this method to be defined
        even though it is only called if no template is specified.

        https://github.com/wagtail/wagtail/blob/8413d00bdd03c447900019961d604186e17d2870/wagtail/core/blocks/base.py#L206
        """
        pass

    def get_api_representation(self, value, context=None):
        """
        Overwrite the default get_api_representation method to include
        additional fields from the EtnaMedia model.

        We use expand_db_html to get any rich text fields as useful HTML,
        rather than the raw database representation.
        """
        return {
            "id": value.id,
            "uuid": value.uuid,
            "file": value.url,
            "alternate_version_link": value.alternate_version_link,
            "alternate_version_type": value.get_alternate_version_type_display(),
            "full_url": value.full_url,
            "type": value.type,
            "mime": value.mime(),
            "title": value.title,
            "date": value.date,
            "description": expand_db_html(value.description),
            "transcript": expand_db_html(value.transcript),
            "chapters": value.api_chapters(),
            "width": value.width,
            "height": value.height,
            "duration": value.duration,
            "subtitles_file": value.subtitles_file_url,
            "subtitles_file_full_url": value.subtitles_file_full_url,
            "chapters_file": value.chapters_file_url,
            "chapters_file_full_url": value.chapters_file_full_url,
        }


class MediaBlock(blocks.StructBlock):
    """
    Embedded media block with a selectable thumbnail image.
    """

    title = blocks.CharBlock(
        required=True,
        help_text="A descriptive title for the media block",
    )
    thumbnail = APIImageChooserBlock(
        rendition_size="fill-960x540",
        required=False,
        help_text="A thumbnail image for the media block",
    )
    media = MediaChooserBlock()

    class Meta:
        help_text = "An embedded audio or video block"
        icon = "play"
        label = "Media"
        group = "Video, audio and downloads"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["src"] = value["media"].sources[0]["src"]
        context["type"] = value["media"].sources[0]["type"]
        return context

    @property
    def admin_label(self):
        return self.meta.label
