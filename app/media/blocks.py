from app.core.blocks.image import APIImageChooserBlock
from wagtail import blocks
from wagtail.rich_text import expand_db_html
from wagtailmedia.blocks import AbstractMediaChooserBlock


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
        chapters = [
            {
                "time": int(chapter.value["time"]),
                "heading": chapter.value["heading"],
                "transcript": expand_db_html(chapter.value["transcript"].source),
            }
            for chapter in value.chapters
        ]
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
            "chapters": sorted(chapters, key=lambda x: x["time"]),
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

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["src"] = value["media"].sources[0]["src"]
        context["type"] = value["media"].sources[0]["type"]
        return context

    @property
    def admin_label(self):
        return self.meta.label
