from django.conf import settings
from django.utils.text import capfirst


def get_public_model_label(model):
    overrides = getattr(settings, "PUBLIC_MODEL_LABEL_OVERRIDES", {})
    try:
        label = overrides[model._meta.label_lower]
    except KeyError:
        label = model._meta.verbose_name
        if label.lower().endswith(" page"):
            label = label[:-5]
    return capfirst(label)
