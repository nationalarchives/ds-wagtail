from django.utils.encoding import force_str

from wagtail.core.fields import RichTextField as BaseRichTextField


class RichTextField(BaseRichTextField):
    def get_searchable_content(self, value):
        """Override to retain HTML markup when indexing content.

        Wagtail's RichTextField strips HTML from indexed content.
        """
        source = force_str(value)
        return [source]
