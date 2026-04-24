from types import SimpleNamespace
from unittest.mock import patch

from app.media.blocks import MediaChooserBlock
from django.test import SimpleTestCase


def _make_media_value(**overrides):
    """Build a minimal valid media SimpleNamespace; tests override only what differs."""
    defaults = dict(
        id=1,
        uuid="media-uuid",
        url="/media/test.mp4",
        alternate_version_link=None,
        get_alternate_version_type_display=lambda: None,
        full_url="https://localhost/media/test.mp4",
        type="video",
        mime=lambda: "video/mp4",
        title="Test media",
        date=None,
        description="",
        transcript="",
        chapters=[],
        width=0,
        height=0,
        duration=60,
        subtitles_file_url=None,
        subtitles_file_full_url=None,
        chapters_file_url=None,
        chapters_file_full_url=None,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_chapter(time, heading, transcript):
    return SimpleNamespace(
        value={
            "time": time,
            "heading": heading,
            "transcript": SimpleNamespace(source=transcript),
        }
    )


class MediaChooserBlockTests(SimpleTestCase):
    @patch(
        "app.media.blocks.expand_db_html",
        side_effect=lambda value: f"expanded::{value}",
    )
    def test_get_api_representation_returns_enriched_media_payload(
        self, mock_expand_db_html
    ):
        block = MediaChooserBlock()
        value = _make_media_value(
            id=3,
            alternate_version_link="https://example.com/audio-described",
            get_alternate_version_type_display=lambda: "Audio Described",
            date="2024-01-01",
            description="<p>Description</p>",
            transcript="<p>Transcript</p>",
            chapters=[
                _make_chapter(20, "Part two", "<p>Later</p>"),
                _make_chapter(10, "Part one", "<p>Earlier</p>"),
            ],
            width=1920,
            height=1080,
            subtitles_file_url="/media/test.vtt",
            subtitles_file_full_url="https://localhost/media/test.vtt",
            chapters_file_url="/media/chapters.vtt",
            chapters_file_full_url="https://localhost/media/chapters.vtt",
        )

        representation = block.get_api_representation(value)

        self.assertEqual(representation["id"], 3)
        self.assertEqual(representation["uuid"], "media-uuid")
        self.assertEqual(representation["description"], "expanded::<p>Description</p>")
        self.assertEqual(representation["transcript"], "expanded::<p>Transcript</p>")
        self.assertEqual(
            representation["chapters"],
            [
                {
                    "time": 10,
                    "heading": "Part one",
                    "transcript": "expanded::<p>Earlier</p>",
                },
                {
                    "time": 20,
                    "heading": "Part two",
                    "transcript": "expanded::<p>Later</p>",
                },
            ],
        )

    @patch(
        "app.media.blocks.expand_db_html",
        side_effect=lambda value: f"expanded::{value}",
    )
    def test_get_api_representation_with_no_chapters_returns_empty_list(
        self, mock_expand_db_html
    ):
        block = MediaChooserBlock()
        value = _make_media_value(
            uuid="no-chapters-uuid",
            url="/media/audio.mp3",
            full_url="https://localhost/media/audio.mp3",
            type="audio",
            mime=lambda: "audio/mpeg",
            title="Audio file",
            duration=120,
        )

        representation = block.get_api_representation(value)

        self.assertEqual(representation["chapters"], [])

    @patch(
        "app.media.blocks.expand_db_html",
        side_effect=lambda value: f"expanded::{value}",
    )
    def test_get_api_representation_coerces_chapter_times_to_int(
        self, mock_expand_db_html
    ):
        block = MediaChooserBlock()

        for raw_times, expected_times in (
            (("2", "1"), [1, 2]),
            (("20", "10"), [10, 20]),
        ):
            with self.subTest(raw_times=raw_times, expected_times=expected_times):
                value = _make_media_value(
                    chapters=[
                        _make_chapter(raw_times[0], "Part two", "<p>Later</p>"),
                        _make_chapter(raw_times[1], "Part one", "<p>Earlier</p>"),
                    ]
                )

                representation = block.get_api_representation(value)

                self.assertEqual(
                    [chapter["time"] for chapter in representation["chapters"]],
                    expected_times,
                )
