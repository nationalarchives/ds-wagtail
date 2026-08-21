from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from app.core.serializers.images import DetailedImageSerializer, ImageSerializer


class DummyFile:
    def __init__(self, url, name=None, size=None):
        self.url = url
        self.name = name or url
        self.size = size

    def __str__(self):
        return self.url


class DummyImage:
    def __init__(
        self,
        alt_file,
        transcription=None,
        translation=None,
        copyright=None,
        alt_heading=None,
    ):
        self.alternative_format = alt_file
        self.transcription = transcription
        self.translation = translation
        self.copyright = copyright
        self._alt_heading = alt_heading or "Transcript with tables"

    def get_transcription_heading_display(self):
        return "Transcript"

    def get_translation_heading_display(self):
        return "Translation"

    def get_alternative_format_heading_display(self):
        return self._alt_heading


class TestDetailedImageSerializerAlternativeFormat(TestCase):
    def setUp(self):
        self.base_media_url = settings.STORAGES["default"]["OPTIONS"]["custom_domain"]
        self.base_repr = {"id": 1, "uuid": "u", "title": "t", "description": "d"}

    def test_alternative_format_file_object_default_full_url(self):
        alt = DummyFile(
            "/images/alternative_formats/table.csv",
            "table.csv",
            2048,
        )
        img = DummyImage(alt)
        with patch.object(
            ImageSerializer, "to_representation", return_value=self.base_repr
        ):
            ser = DetailedImageSerializer()
            rep = ser.to_representation(img)

        self.assertIn("alternative_format", rep)
        self.assertIsInstance(rep["alternative_format"], dict)
        self.assertEqual(rep["alternative_format"]["url"], alt.url)
        self.assertEqual(rep["alternative_format"]["file_type"], "csv")
        self.assertEqual(rep["alternative_format"]["file_size"], 2048)

    def test_alternative_format_file_object_with_full_url(self):
        alt = DummyFile("/path/table.xlsx", "path/table.xlsx")
        img = DummyImage(alt)
        with patch.object(
            ImageSerializer, "to_representation", return_value=self.base_repr
        ):
            ser = DetailedImageSerializer()
            rep = ser.to_representation(img)

        self.assertEqual(rep["alternative_format"]["url"], alt.url)
        self.assertEqual(rep["alternative_format"]["file_type"], "xlsx")

    def test_file_with_multiple_dots(self):
        alt = DummyFile("/path/my.file.name.csv", "my.file.name.csv")
        img = DummyImage(alt)
        with patch.object(
            ImageSerializer, "to_representation", return_value=self.base_repr
        ):
            ser = DetailedImageSerializer()
            rep = ser.to_representation(img)

        self.assertEqual(rep["alternative_format"]["file_type"], "csv")

    def test_url_with_query_string(self):
        alt = DummyFile("/path/table.csv?ver=1", "table.csv?ver=1")
        img = DummyImage(alt)
        with patch.object(
            ImageSerializer, "to_representation", return_value=self.base_repr
        ):
            ser = DetailedImageSerializer()
            rep = ser.to_representation(img)

        self.assertEqual(rep["alternative_format"]["file_type"], "csv")

    def test_no_extension_returns_none(self):
        alt = DummyFile("/path/file", "file")
        img = DummyImage(alt)
        with patch.object(
            ImageSerializer, "to_representation", return_value=self.base_repr
        ):
            ser = DetailedImageSerializer()
            rep = ser.to_representation(img)

        self.assertIsNone(rep["alternative_format"]["file_type"])

    def test_uppercase_extension_normalized(self):
        alt = DummyFile("/path/table.CSV", "table.CSV")
        img = DummyImage(alt)
        with patch.object(
            ImageSerializer, "to_representation", return_value=self.base_repr
        ):
            ser = DetailedImageSerializer()
            rep = ser.to_representation(img)

        self.assertEqual(rep["alternative_format"]["file_type"], "csv")

    def test_missing_size_returns_none(self):
        alt = DummyFile("/path/table.csv", "table.csv")
        img = DummyImage(alt)
        with patch.object(
            ImageSerializer, "to_representation", return_value=self.base_repr
        ):
            ser = DetailedImageSerializer()
            rep = ser.to_representation(img)

        self.assertIsNone(rep["alternative_format"]["file_size"])
