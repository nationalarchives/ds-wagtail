from types import SimpleNamespace
from unittest.mock import patch

from app.media.blocks import MediaChooserBlock
from django.test import SimpleTestCase


class MediaChooserBlockTests(SimpleTestCase):
    @patch(
        "app.media.blocks.expand_db_html",
        side_effect=lambda value: f"expanded::{value}",
    )
    def test_get_api_representation_returns_enriched_media_payload(
        self, mock_expand_db_html
    ):
        block = MediaChooserBlock()
        value = SimpleNamespace(
            id=3,
            uuid="media-uuid",
            url="/media/test.mp4",
            alternate_version_link="https://example.com/audio-described",
            get_alternate_version_type_display=lambda: "Audio Described",
            full_url="https://localhost/media/test.mp4",
            type="video",
            mime=lambda: "video/mp4",
            title="Test media",
            date="2024-01-01",
            description="<p>Description</p>",
            transcript="<p>Transcript</p>",
            chapters=[
                SimpleNamespace(
                    value={
                        "time": 20,
                        "heading": "Part two",
                        "transcript": SimpleNamespace(source="<p>Later</p>"),
                    }
                ),
                SimpleNamespace(
                    value={
                        "time": 10,
                        "heading": "Part one",
                        "transcript": SimpleNamespace(source="<p>Earlier</p>"),
                    }
                ),
            ],
            width=1920,
            height=1080,
            duration=60,
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
        self.assertEqual(mock_expand_db_html.call_count, 4)

    @patch(
        "app.media.blocks.expand_db_html",
        side_effect=lambda value: f"expanded::{value}",
    )
    def test_get_api_representation_with_no_chapters_returns_empty_list(
        self, mock_expand_db_html
    ):
        block = MediaChooserBlock()
        value = SimpleNamespace(
            id=1,
            uuid="no-chapters-uuid",
            url="/media/audio.mp3",
            alternate_version_link=None,
            get_alternate_version_type_display=lambda: None,
            full_url="https://localhost/media/audio.mp3",
            type="audio",
            mime=lambda: "audio/mpeg",
            title="Audio file",
            date=None,
            description="",
            transcript="",
            chapters=[],
            width=0,
            height=0,
            duration=120,
            subtitles_file_url=None,
            subtitles_file_full_url=None,
            chapters_file_url=None,
            chapters_file_full_url=None,
        )

        representation = block.get_api_representation(value)

        self.assertEqual(representation["chapters"], [])
