from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.admin.viewsets.chooser import ChooserViewSet
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.images import get_image_model_string


class PartnerLogo(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    logo = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="+",
    )
    logo_dark = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    def __str__(self):
        return self.name

    panels = [
        FieldPanel("name"),
        FieldPanel("logo"),
        FieldPanel("logo_dark"),
    ]


class PartnerLogoModelViewSet(ModelViewSet):
    model = PartnerLogo
    form_fields = [
        "name",
        "logo",
        "logo_dark",
    ]
    icon = "image"
    menu_label = "Partner Logos"
    menu_name = "partner_logos"
    add_to_admin_menu = True


partner_logo_modelviewset = PartnerLogoModelViewSet("partner_logos")


class PartnerLogoChooserViewSet(ChooserViewSet):
    model = PartnerLogo
    icon = "image"
    page_title = "Partner Logo Chooser"
    choose_one_text = "Choose a partner logo"
    choose_many_text = "Choose partner logos"


partner_logo_chooserviewset = PartnerLogoChooserViewSet("partner_logo_chooser")
