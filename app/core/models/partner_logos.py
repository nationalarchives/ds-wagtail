from django.db import models
from wagtail.admin.viewsets.model import ModelViewSet
from django.core.exceptions import ValidationError


def validate_svg_file(value):
    if not value.name.endswith('.svg'):
        raise ValidationError("The file must be an SVG file.")


class PartnerLogo(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    svg_file = models.FileField(
        upload_to='partner_logos/', blank=True, null=True, help_text="Upload the SVG file for the partner logo.", verbose_name="SVG File",
        validators=[validate_svg_file]
    )
    raster_file = models.ImageField(
        upload_to='partner_logos/', blank=True, null=True, help_text="Upload a raster image for the partner logo."
    )
    alt_text = models.CharField(max_length=255, blank=False, null=False)

    def clean(self):
        if not self.svg_file and not self.raster_file:
            raise ValidationError("At least one file (SVG or raster) must be provided.")
        if self.svg_file and self.raster_file:
            raise ValidationError("Please provide either an SVG file or a raster image, not both.")
        return super().clean()

    def __str__(self):
        return self.name


class PartnerLogoViewSet(ModelViewSet):
    model = PartnerLogo
    form_fields = ["name", "svg_file", "raster_file", "alt_text"]
    icon = "image"
    menu_label = "Partner Logos"
    menu_name = "partner_logos"
    add_to_admin_menu = True


partner_logo_viewset = PartnerLogoViewSet("partner_logos")
