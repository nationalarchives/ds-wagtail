import logging
import time
from tempfile import SpooledTemporaryFile

from django.conf import settings
from django.core.files import File
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.images.models import (
    IMAGE_FORMAT_EXTENSIONS,
    AbstractImage,
    AbstractRendition,
    Filter,
)
from wagtail.search import index

from etna.ciim.fields import RecordField
from etna.ciim.serializers import RecordSerializer
from etna.core.serializers import RichTextSerializer

logger = logging.getLogger(__name__)


DEFAULT_SENSITIVE_IMAGE_WARNING = (
    "This image contains content which some people may find offensive or distressing."
)


class TranscriptionHeadingChoices(models.TextChoices):
    TRANSCRIPT = "transcript", _("Transcript")
    PARTIAL_TRANSCRIPTION = "partial-transcript", _("Partial transcript")


class TranslationHeadingChoices(models.TextChoices):
    TRANSLATION = "translation", _("Translation")
    MODERN_ENGLISH = "modern-english", _("Modern English")


class CustomImage(ClusterableModel, AbstractImage):
    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
        help_text=_(
            "The descriptive name of the image. If this image features in a highlights gallery, this title will be visible on the page."
        ),
    )

    copyright = RichTextField(
        verbose_name=_("copyright"),
        blank=True,
        max_length=200,
        help_text=_(
            "Credit for images not owned by TNA. Do not include the copyright symbol."
        ),
        features=settings.INLINE_RICH_TEXT_FEATURES,
    )

    transcription_heading = models.CharField(
        verbose_name=_("transcript heading"),
        max_length=30,
        choices=TranscriptionHeadingChoices.choices,
        default=TranscriptionHeadingChoices.TRANSCRIPT,
    )

    transcription = RichTextField(
        verbose_name=_("transcript"),
        features=["bold", "italic", "ol", "ul"],
        blank=True,
        max_length=1500,
        help_text=_("If the image contains text consider adding a transcript."),
    )

    translation_heading = models.CharField(
        verbose_name=_("translation heading"),
        max_length=30,
        choices=TranslationHeadingChoices.choices,
        default=TranslationHeadingChoices.TRANSLATION,
        help_text=_(
            'If the original transcription language is some earlier form of English, choose "Modern English". If not, choose “Translation”.'
        ),
    )

    translation = RichTextField(
        verbose_name=_("translation"),
        features=["bold", "italic", "ol", "ul"],
        blank=True,
        max_length=1500,
        help_text=_(
            "An optional English / Modern English translation of the transcription."
        ),
    )

    search_fields = AbstractImage.search_fields + [
        index.SearchField("transcription", boost=1),
        index.SearchField("translation", boost=1),
        index.SearchField("copyright"),
    ]

    api_fields = [
        APIField("title"),
        APIField("copyright"),
        APIField("description"),
        APIField("transcription_heading"),
        APIField("transcription", serializer=RichTextSerializer()),
        APIField("translation_heading"),
        APIField("translation", serializer=RichTextSerializer()),
    ]

    @property
    def sensitive_image_warning(self):
        return (
            self.custom_sensitive_image_warning.strip()
            or DEFAULT_SENSITIVE_IMAGE_WARNING
        )

    admin_form_fields = [
        "title",
        "file",
        "description",
        "collection",
        "copyright",
        "tags",
        "focal_point_x",
        "focal_point_y",
        "focal_point_width",
        "focal_point_height",
        "transcription_heading",
        "transcription",
        "translation_heading",
        "translation",
    ]

    def generate_rendition_file(self, filter: Filter, *, source: File = None) -> File:
        """
        this has been over-ridden form the wagtail version because the truncation of file names by 60 chars
        is causing image file names to not be unique

        Generates an in-memory image matching the supplied ``filter`` value
        and focal point value from this object, wraps it in a ``File`` object
        with a suitable filename, and returns it. The return value is used
        as the ``file`` field value for rendition objects saved by
        ``AbstractImage.create_rendition()``.

        If the contents of ``self.file`` has already been read into memory, the
        ``source`` keyword can be used to provide a reference to the in-memory
        ``File``, bypassing the need to reload the image contents from storage.

        NOTE: The responsibility of generating the new image from the original
        falls to the supplied ``filter`` object. If you want to do anything
        custom with rendition images (for example, to preserve metadata from
        the original image), you might want to consider swapping out ``filter``
        for an instance of a custom ``Filter`` subclass of your design.
        """

        cache_key = filter.get_cache_key(self)

        logger.debug(
            "Generating '%s' rendition for image %d",
            filter.spec,
            self.pk,
        )

        start_time = time.time()

        try:
            generated_image = filter.run(
                self,
                SpooledTemporaryFile(max_size=settings.FILE_UPLOAD_MAX_MEMORY_SIZE),
                source=source,
            )

            logger.debug(
                "Generated '%s' rendition for image %d in %.1fms",
                filter.spec,
                self.pk,
                (time.time() - start_time) * 1000,
            )
        except:  # noqa:B901,E722
            logger.debug(
                "Failed to generate '%s' rendition for image %d",
                filter.spec,
                self.pk,
            )
            raise
        # Generate filename
        # input_filename = os.path.basename(self.file.name)
        # input_filename_without_extension, input_extension = os.path.splitext(
        #    input_filename
        # )
        output_filename_without_extension = str(self.id)
        output_extension = (
            filter.spec.replace("|", ".")
            + IMAGE_FORMAT_EXTENSIONS[generated_image.format_name]
        )
        if cache_key:
            output_extension = cache_key + "." + output_extension

        # Truncate filename to prevent it going over 60 chars
        # output_filename_without_extension = input_filename_without_extension[
        #    : (59 - len(output_extension))
        # ]
        output_filename = output_filename_without_extension + "." + output_extension

        return File(generated_image.f, name=output_filename)


class CustomImageRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage, on_delete=models.CASCADE, related_name="renditions"
    )

    @property
    def full_url(self):
        url = self.url
        if url.startswith("/"):
            if (
                hasattr(settings, "WAGTAILAPI_IMAGES_BASE_URL")
                and settings.WAGTAILAPI_IMAGES_BASE_URL
            ):
                url = settings.WAGTAILAPI_IMAGES_BASE_URL + url
            elif hasattr(settings, "WAGTAILADMIN_BASE_URL"):
                url = settings.WAGTAILADMIN_BASE_URL + url
        return url

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
