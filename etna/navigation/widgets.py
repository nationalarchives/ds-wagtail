from django.forms.widgets import Select
from django.urls.resolvers import get_resolver
from django.utils.functional import cached_property


class NamedURLSelect(Select):
    def __init__(self, attrs=None):
        super().__init__(attrs, self.url_choices)

    @cached_property
    def url_choices(self):
        choices = [("", "---")]
        resolver = get_resolver()
        for pattern in resolver.url_patterns:
            if getattr(pattern, "name", None) and not getattr(
                pattern.pattern, "converters", None
            ):
                choices.append((pattern.name, str(pattern.pattern)))
        return choices
