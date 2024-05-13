# Generated by Django 4.1.7 on 2023-03-16 21:53

from django.db import migrations, models
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("images", "0005_alter_customimage_file_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customimage",
            name="transcription_language",
        ),
        migrations.AddField(
            model_name="customimage",
            name="copyright",
            field=models.CharField(
                blank=True,
                help_text="Credit for images not owned by TNA. Do not include the copyright symbol.",
                max_length=200,
                verbose_name="copyright",
            ),
        ),
        migrations.AddField(
            model_name="customimage",
            name="transcription_heading",
            field=models.CharField(
                choices=[
                    ("transcript", "Transcript"),
                    ("partial-transcript", "Partial transcript"),
                ],
                default="transcript",
                max_length=30,
                verbose_name="transcript heading",
            ),
        ),
        migrations.AddField(
            model_name="customimage",
            name="translation_heading",
            field=models.CharField(
                choices=[
                    ("translation", "Translation"),
                    ("modern-english", "Modern English"),
                ],
                default="translation",
                help_text='If the original transcription language is some earlier form of English, choose "Modern English". If not, choose “Translation”.',
                max_length=30,
                verbose_name="translation heading",
            ),
        ),
        migrations.AlterField(
            model_name="customimage",
            name="description",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="This text will appear in highlights galleries. A 100-300 word description of the story of the record and why it is significant.",
                max_length=900,
                verbose_name="description",
            ),
        ),
        migrations.AlterField(
            model_name="customimage",
            name="title",
            field=models.CharField(
                help_text="The descriptive name of the image. If this image features in a highlights gallery, this title will be visible on the page.",
                max_length=255,
                verbose_name="title",
            ),
        ),
        migrations.AlterField(
            model_name="customimage",
            name="transcription",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="If the image contains text consider adding a transcript.",
                max_length=1500,
                verbose_name="transcript",
            ),
        ),
        migrations.AlterField(
            model_name="customimage",
            name="translation",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="An optional English / Modern English translation of the transcription.",
                max_length=1500,
                verbose_name="translation",
            ),
        ),
    ]