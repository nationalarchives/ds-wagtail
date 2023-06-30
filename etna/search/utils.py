from django.conf import settings
from django.utils.text import capfirst


def get_public_page_type_label(model):
    try:
        return capfirst(
            settings.PUBLIC_PAGE_TYPE_LABEL_OVERRIDES[model._meta.label_lower]
        )
    except (AttributeError, KeyError):
        pass

    label = capfirst(model._meta.verbose_name)
    if label.lower().endswith(" page"):
        return label[:-5]
    return label
