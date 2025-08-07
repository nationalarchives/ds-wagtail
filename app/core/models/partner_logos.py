from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.admin.viewsets.chooser import ChooserViewSet
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.images import get_image_model_string


def validate_svg_file(value):
    if not value.name.endswith(".svg"):
        raise ValidationError("The file must be an SVG file.")


class PartnerLogo(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    svg_file = models.FileField(
        upload_to="partner_logos/",
        blank=True,
        null=True,
        help_text="Upload the SVG file for the partner logo.",
        verbose_name="SVG File",
        validators=[validate_svg_file],
    )
    raster_file = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    alt_text = models.CharField(max_length=255, blank=False, null=False)

    def clean(self):
        if not self.svg_file and not self.raster_file:
            raise ValidationError("At least one file (SVG or raster) must be provided.")
        if self.svg_file and self.raster_file:
            raise ValidationError(
                "Please provide either an SVG file or a raster image, not both."
            )
        return super().clean()

    def __str__(self):
        return self.name

    panels = [
        FieldPanel("name"),
        FieldPanel("svg_file"),
        FieldPanel("raster_file"),
        FieldPanel("alt_text"),
    ]


class PartnerLogoModelViewSet(ModelViewSet):
    model = PartnerLogo
    form_fields = ["name", "svg_file", "raster_file", "alt_text"]
    icon = "image"
    menu_label = "Partner Logos"
    menu_name = "partner_logos"
    add_to_admin_menu = True


partner_logo_modelviewset = PartnerLogoModelViewSet("partner_logos")


class PartnerLogoChooserViewSet(ChooserViewSet):
    model = PartnerLogo
    icon = "image"
    page_title = "Partner Logo Chooser"
    base_form_class = PartnerLogo
    choose_one_text = "Choose a partner logo"
    choose_many_text = "Choose partner logos"


partner_logo_chooserviewset = PartnerLogoChooserViewSet("partner_logo_chooser")
