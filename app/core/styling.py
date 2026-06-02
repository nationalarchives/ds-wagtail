from django.db import models


class BrandColourChoices(models.TextChoices):
    """
    This model is a list of our brand accent colours, which can be used
    on various components on the site.
    """

    NONE = "none", "None"
    BLACK = "black", "Black"
    PINK = "pink", "Pink"
    ORANGE = "orange", "Orange"
    YELLOW = "yellow", "Yellow"
    GREEN = "green", "Green"
    BLUE = "blue", "Blue"


class HeroColourChoices(models.TextChoices):
    """
    This model is a list of our "hero" colour choices, which can be used
    on the hero component.
    """

    NONE = "none", "None"
    CONTRAST = "contrast", "Contrast"
    TINT = "tint", "Tint"
    ACCENT = "accent", "Accent"


class HeroLayoutChoices(models.TextChoices):
    """
    This model is a list of our "hero" layouts, which can be used
    on the hero component.
    """

    DEFAULT = "default", "Default"
    SHIFT = "shift", "Shifted"
    SPLIT = "split", "Split"
