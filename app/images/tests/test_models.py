from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from app.images.models import AlternativeFormatHeadingChoices, CustomImage


class TestCustomImageAlternativeFormatValidation(TestCase):
    @staticmethod
    def image_upload_file():
        return SimpleUploadedFile(
            "test.gif",
            (
                b"GIF89a\x01\x00\x01\x00\x80\x00\x00"
                b"\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00"
                b",\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
            ),
            content_type="image/gif",
        )

    def test_validation_allows_csv_and_xlsx_files(self):
        csv_image = CustomImage(
            title="CSV alternative format",
            file=self.image_upload_file(),
            alternative_format_heading=AlternativeFormatHeadingChoices.TRANSCRIPT_WITH_TABLES,
            alternative_format=SimpleUploadedFile("table.csv", b"a,b\n1,2\n"),
        )
        xlsx_image = CustomImage(
            title="XLSX alternative format",
            file=self.image_upload_file(),
            alternative_format_heading=AlternativeFormatHeadingChoices.TRANSCRIPT_WITH_TABLES,
            alternative_format=SimpleUploadedFile(
                "table.xlsx",
                b"xlsx-content",
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
        )

        csv_image.full_clean()
        xlsx_image.full_clean()

    def test_validation_rejects_other_file_extensions(self):
        image = CustomImage(
            title="Invalid alternative format",
            file=self.image_upload_file(),
            alternative_format=SimpleUploadedFile("table.pdf", b"pdf-content"),
        )

        with self.assertRaises(ValidationError) as context:
            image.full_clean()

        self.assertIn("File extension", str(context.exception))
        self.assertIn("csv", str(context.exception))
        self.assertIn("xlsx", str(context.exception))

    def test_validation_requires_heading_when_file_is_uploaded(self):
        image = CustomImage(
            title="Missing heading",
            file=self.image_upload_file(),
            alternative_format=SimpleUploadedFile("table.csv", b"a,b\n1,2\n"),
        )

        with self.assertRaises(ValidationError) as context:
            image.full_clean()

        self.assertIn("alternative_format_heading", context.exception.message_dict)

    def test_validation_requires_file_when_heading_is_selected(self):
        image = CustomImage(
            title="Missing file",
            file=self.image_upload_file(),
            alternative_format_heading=AlternativeFormatHeadingChoices.TRANSCRIPT_WITH_TABLES,
        )

        with self.assertRaises(ValidationError) as context:
            image.full_clean()

        self.assertIn("alternative_format", context.exception.message_dict)
