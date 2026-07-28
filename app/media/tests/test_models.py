import json

from django.core.exceptions import ValidationError
from django.db import connection
from django.test import TestCase

from app.media.blocks import (
    CHAPTER_TIME_VALIDATION_MESSAGE,
    ChapterTimeBlock,
    MediaChooserBlock,
    normalise_chapter_time_for_display,
)
from app.media.fields import MediaDurationFormField
from app.media.models import EtnaMedia, MediaChapterSectionBlock


class TestMediaChapterSectionBlock(TestCase):
    def test_duration_form_field_uses_hhmmss_input_guidance(self):
        field = MediaDurationFormField(required=False)

        self.assertEqual(
            field.help_text,
            "Enter duration as HH:MM:SS.",
        )
        self.assertEqual(
            field.widget.attrs["placeholder"],
            "00:00:00",
        )
        self.assertEqual(field.prepare_value(3723), "01:02:03")

    def test_duration_form_field_rejects_non_hhmmss_input(self):
        field = MediaDurationFormField(required=False)

        with self.assertRaises(ValidationError) as invalid_duration:
            field.clean("12:34")

        self.assertIn(
            "Duration must be in HH:MM:SS format.",
            str(invalid_duration.exception),
        )

    def test_duration_form_field_converts_hhmmss_to_seconds(self):
        field = MediaDurationFormField(required=False)

        self.assertEqual(field.clean("01:02:03"), 3723)

    def test_duration_hhmmss_is_stored_as_seconds(self):
        media = EtnaMedia.objects.create(
            title="Test media",
            file="media/test.mp4",
            type="video",
            duration="01:02:03",
            width=1920,
            height=1080,
            thumbnail="media/test.jpg",
        )

        media.refresh_from_db()
        self.assertEqual(media.duration, 3723)

    def test_api_duration_returns_seconds(self):
        media = EtnaMedia(
            title="Test media",
            file="media/test.mp4",
            type="video",
            duration="01:02:03",
            width=1920,
            height=1080,
            thumbnail="media/test.jpg",
            description="",
            transcript="",
        )

        self.assertEqual(media.api_duration(), 3723)

    def test_media_block_api_representation_uses_duration_seconds(self):
        media = EtnaMedia(
            title="Test media",
            file="media/test.mp4",
            type="video",
            duration="01:02:03",
            width=1920,
            height=1080,
            thumbnail="media/test.jpg",
            description="",
            transcript="",
        )

        representation = MediaChooserBlock().get_api_representation(media)

        self.assertEqual(representation["duration"], 3723)

    def test_duration_mmss_is_rejected(self):
        media = EtnaMedia(
            title="Test media",
            file="media/test.mp4",
            type="video",
            duration="12:34",
            width=1920,
            height=1080,
            thumbnail="media/test.jpg",
        )

        with self.assertRaises(ValidationError) as invalid_duration:
            media.full_clean()

        self.assertIn(
            "Duration must be in HH:MM:SS format.",
            str(invalid_duration.exception),
        )

    def test_duration_rejects_invalid_time_string(self):
        media = EtnaMedia(
            title="Test media",
            file="media/test.mp4",
            type="video",
            duration="not-a-time",
            width=1920,
            height=1080,
            thumbnail="media/test.jpg",
        )

        with self.assertRaises(ValidationError) as invalid_duration:
            media.full_clean()

        self.assertIn(
            "Duration must be in HH:MM:SS format.",
            str(invalid_duration.exception),
        )

    def test_duration_float_is_rejected(self):
        media = EtnaMedia(
            title="Test media",
            file="media/test.mp4",
            type="video",
            duration=12.34,
            width=1920,
            height=1080,
            thumbnail="media/test.jpg",
        )

        with self.assertRaises(ValidationError) as invalid_duration:
            media.full_clean()

        self.assertIn(
            "Duration must be in HH:MM:SS format.",
            str(invalid_duration.exception),
        )

    def test_duration_negative_integer_is_rejected(self):
        media = EtnaMedia(
            title="Test media",
            file="media/test.mp4",
            type="video",
            duration=-1,
            width=1920,
            height=1080,
            thumbnail="media/test.jpg",
        )

        with self.assertRaises(ValidationError) as invalid_duration:
            media.full_clean()

        self.assertIn(
            "Duration must be greater than or equal to 0.",
            str(invalid_duration.exception),
        )

    def test_chapter_times_are_stored_as_seconds_but_rendered_as_hhmmss(self):
        media = EtnaMedia.objects.create(
            title="Test media",
            file="media/test.mp4",
            type="video",
            duration=10,
            width=1920,
            height=1080,
            thumbnail="media/test.jpg",
            chapters=[
                (
                    "chapter",
                    {
                        "time": "01:02:03",
                        "heading": "Intro",
                        "transcript": "",
                    },
                )
            ],
        )

        media.refresh_from_db()
        chapter_value = media.chapters[0].value

        self.assertEqual(chapter_value["time"], "01:02:03")
        self.assertEqual(
            MediaChapterSectionBlock().get_form_state(chapter_value)["time"],
            "01:02:03",
        )

        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT chapters FROM {EtnaMedia._meta.db_table} WHERE id = %s",
                [media.id],
            )
            stored_value = cursor.fetchone()[0]

        if isinstance(stored_value, str):
            stored_value = json.loads(stored_value)

        self.assertEqual(stored_value[0]["value"]["time"], 3723)
        self.assertEqual(media.api_chapters()[0]["time"], 3723)

    def test_api_chapters_returns_sorted_seconds(self):
        media = EtnaMedia.objects.create(
            title="Test media",
            file="media/test.mp4",
            type="video",
            duration=10,
            width=1920,
            height=1080,
            thumbnail="media/test.jpg",
            chapters=[
                (
                    "chapter",
                    {
                        "time": "00:00:05",
                        "heading": "Second",
                        "transcript": "",
                    },
                ),
                (
                    "chapter",
                    {
                        "time": "00:00:02",
                        "heading": "First",
                        "transcript": "",
                    },
                ),
            ],
        )

        self.assertEqual([chapter["time"] for chapter in media.api_chapters()], [2, 5])
        self.assertTrue(
            all(isinstance(chapter["time"], int) for chapter in media.api_chapters())
        )

    def test_chapter_time_clean_rejects_out_of_range_units(self):
        block = ChapterTimeBlock()

        with self.assertRaises(ValidationError) as out_of_range_minutes:
            block.clean("00:99:00")
        self.assertIn(
            CHAPTER_TIME_VALIDATION_MESSAGE, str(out_of_range_minutes.exception)
        )
        self.assertIn("'00:99:00'", str(out_of_range_minutes.exception))

        with self.assertRaises(ValidationError) as out_of_range_seconds:
            block.clean("00:00:99")
        self.assertIn(
            CHAPTER_TIME_VALIDATION_MESSAGE, str(out_of_range_seconds.exception)
        )
        self.assertIn("'00:00:99'", str(out_of_range_seconds.exception))

        with self.assertRaises(ValidationError) as malformed_time:
            block.clean("not-a-time")
        self.assertIn(CHAPTER_TIME_VALIDATION_MESSAGE, str(malformed_time.exception))
        self.assertIn("'not-a-time'", str(malformed_time.exception))

    def test_chapter_time_display_normalisation_preserves_invalid_values(self):
        self.assertEqual(normalise_chapter_time_for_display("00:62:5123"), "00:62:5123")
        self.assertEqual(normalise_chapter_time_for_display("not-a-time"), "not-a-time")

    def test_chapter_time_display_normalisation_handles_numeric_values(self):
        self.assertEqual(normalise_chapter_time_for_display(5), "00:00:05")
        self.assertEqual(normalise_chapter_time_for_display("5"), "00:00:05")

    def test_three_digit_hour_time_is_stored_as_correct_seconds(self):
        media = EtnaMedia.objects.create(
            title="Test media",
            file="media/test.mp4",
            type="video",
            duration=10,
            width=1920,
            height=1080,
            thumbnail="media/test.jpg",
            chapters=[
                (
                    "chapter",
                    {
                        "time": "123:00:00",
                        "heading": "Long form section",
                        "transcript": "",
                    },
                )
            ],
        )

        media.refresh_from_db()

        # Frontend/editor value should remain HH:MM:SS
        chapter_value = media.chapters[0].value
        self.assertEqual(chapter_value["time"], "123:00:00")

        # Backend/storage/API value should be seconds
        expected_seconds = 123 * 3600
        self.assertEqual(media.api_chapters()[0]["time"], expected_seconds)

        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT chapters FROM {EtnaMedia._meta.db_table} WHERE id = %s",
                [media.id],
            )
            stored_value = cursor.fetchone()[0]

        if isinstance(stored_value, str):
            stored_value = json.loads(stored_value)

        self.assertEqual(stored_value[0]["value"]["time"], expected_seconds)
