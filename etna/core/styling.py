from django.db import models
from django.utils.translation import gettext_lazy as _


class BrandColourChoices(models.TextChoices):
    """
    This model is a list of our brand accent colours, which can be used
    on various components on the site.
    """

    NONE = "none", _("None")
    BLACK = "black", _("Black")
    PINK = "pink", _("Pink")
    ORANGE = "orange", _("Orange")
    YELLOW = "yellow", _("Yellow")
    GREEN = "green", _("Green")
    BLUE = "blue", _("Blue")


class HeroColourChoices(models.TextChoices):
    """
    This model is a list of our "hero" colour choices, which can be used
    on the hero component.
    """

    NONE = "none", _("None")
    CONTRAST = "contrast", _("Contrast")
    TINT = "tint", _("Tint")
    ACCENT = "accent", _("Accent")


class HeroLayoutChoices(models.TextChoices):
    """
    This model is a list of our "hero" layouts, which can be used
    on the hero component.
    """

    DEFAULT = "default", _("Default")
    SHIFT = "shift", _("Shifted")
    SPLIT = "split", _("Split")
