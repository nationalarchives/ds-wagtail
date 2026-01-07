from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError


class LinkBlockStructValue(blocks.StructValue):
    """
    Provides convenience methods for accessing link data from internal pages or 
    external URLs.

    Methods:
    - url(): Returns the URL (from page or external_link)
    - text(): Returns the link text (custom title or page title)
    - is_page(): Returns True if this is an internal page link
    """

    def url(self):
        if page := self.get("page"):
            return page.url

        if external_link := self.get("external_link"):
            return external_link

        return ""

    def text(self):
        if self.get("page") and not self.get("title"):
            return self.get("page").title
        if title := self.get("title"):
            return title
        return ""

    def is_page(self):
        return bool(self.get("page"))


class LinkValidationMixin:
    """
    Ensure exactly one link type (internal page or external URL) is populated.
    """

    def clean(self, value):
        struct_value = super().clean(value)

        errors = {}
        page = value.get("page")
        external_link = value.get("external_link")

        if not page and not external_link:
            error = ErrorList(
                [ValidationError("You must specify either a page or an external link")]
            )
            errors["page"] = errors["external_link"] = error

        if page and external_link:
            error = ErrorList(
                [
                    ValidationError(
                        "You must specify either a page or an external link, not both"
                    )
                ]
            )
            errors["external_link"] = errors["page"] = error

        if errors:
            raise StructBlockValidationError(errors)
        return struct_value


class InternalLinkBlock(LinkValidationMixin, blocks.StructBlock):
    """
    An link block supporting internal pages with optional custom title.
    """

    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(
        help_text="Leave blank to use the page's own title",
        required=False,
        label="Link text",
    )

    def get_api_representation(self, value, context=None):
        return {
            "url": value.url(),
            "text": value.text(),
            "is_page": value.is_page(),
        }

    class Meta:
        value_class = LinkBlockStructValue


class LinkBlock(InternalLinkBlock):
    """
    A flexible link block supporting both internal pages and external URLs.
    """

    external_link = blocks.URLBlock(required=False)

    class Meta:
        value_class = LinkBlockStructValue

    def clean(self, value):
        """
        Additional validation to ensure that a link title is specified for external links
        """
        struct_value = super().clean(value)

        errors = {}
        external_link = value.get("external_link")

        if not value.get("title") and external_link:
            error = ErrorList(
                [ValidationError("You must specify the link title for external links")]
            )
            errors["title"] = error

        if errors:
            raise StructBlockValidationError(errors)
        return struct_value