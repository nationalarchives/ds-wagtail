from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from app.images.models import CustomImage


class TestCustomImageAlternativeFormatValidation(TestCase):
    def test_validation_allows_csv_and_xlsx_files(self):
        csv_image = CustomImage(
            title="CSV alternative format",
            file="images/test.jpg",
            width=1,
            height=1,
            alternative_format=SimpleUploadedFile("table.csv", b"a,b\n1,2\n"),
        )
        xlsx_image = CustomImage(
            title="XLSX alternative format",
            file="images/test.jpg",
            width=1,
            height=1,
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
            file="images/test.jpg",
            width=1,
            height=1,
            alternative_format=SimpleUploadedFile("table.pdf", b"pdf-content"),
        )

        with self.assertRaises(ValidationError) as context:
            image.full_clean()

        self.assertIn("File extension", str(context.exception))
        self.assertIn("csv", str(context.exception))
        self.assertIn("xlsx", str(context.exception))