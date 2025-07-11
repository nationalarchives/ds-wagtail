from django.utils.text import slugify
from wagtail import blocks


class SectionDepthAwareStructBlock(blocks.StructBlock):
    """
    A StructBlock that includes "content_depth" and "heading_level" values in
    the context that reflect the depth of the block within the StreamField
    value.

    If the block itself has a heading, a "heading_id" value will also be added
    to the context, which can be used as a HTML ID value in the template.

    NOTE: Render blocks with {% include_block %} to ensure the values are
    passed through the parent level.
    """

    def get_heading_id(self, value, heading_level: str = "h2"):
        if heading := value.get("heading"):
            return f"{heading_level}.{slugify(heading)}"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        try:
            content_depth = context["content_depth"] + 1
        except (KeyError, TypeError, ValueError):
            content_depth = 1

        heading_level = f"h{content_depth + 1}"
        context.update(
            content_depth=content_depth,
            heading_level=heading_level,
            heading_id=self.get_heading_id(value, heading_level),
        )
        return context

    @property
    def admin_label(self):
        return self.meta.label
