import json

from django.core.exceptions import ValidationError
from django.db import connection
from django.test import TestCase

from app.media.blocks import CHAPTER_TIME_VALIDATION_MESSAGE, ChapterTimeBlock
from app.media.models import EtnaMedia, MediaChapterSectionBlock


class TestMediaChapterSectionBlock(TestCase):
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
