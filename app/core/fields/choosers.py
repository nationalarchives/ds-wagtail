from django.db import models


class PartnerLogoField(models.ForeignKey):
    """
    A custom field for adding Partner logos to a page.
    This field is a ForeignKey to the PartnerLogo model.
    """

    def __init__(self, *args, **kwargs):
        kwargs["to"] = "core.PartnerLogo"
        kwargs["on_delete"] = models.SET_NULL
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop("to", None)  # Remove 'to' from kwargs
        return name, path, args, kwargs
