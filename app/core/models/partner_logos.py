from django.db import models
from wagtail.admin.viewsets.model import ModelViewSet

class PartnerLogo(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    svg_code = models.TextField(blank=False, null=False)
    alt_text = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.name

class PartnerLogoViewSet(ModelViewSet):
    model = PartnerLogo
    form_fields = ["name", "svg_code", "alt_text"]
    icon = "image"
    menu_label = "Partner Logos"
    menu_name = "partner_logos"
    add_to_admin_menu = True

partner_logo_viewset = PartnerLogoViewSet("partner_logos")