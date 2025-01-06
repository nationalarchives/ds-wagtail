from typing import Any, Optional, Sequence

from django.utils.functional import cached_property
from wagtail import blocks
from wagtail.blocks.list_block import ListValue
from wagtail.coreutils import resolve_model_string
from wagtail.models import Page, PageBase
from wagtail.query import PageQuerySet

from .page_chooser import APIPageChooserBlock


class PageListBlock(blocks.ListBlock):
    """
    A specialized ListBlock for selecting a list of pages. In addition to
    defining the ``child_block`` automatically, it also automatically filters
    out draft and/or private pages when rendering, and provides the
    ``select_related`` and ``prefetch_related`` options to allow related data
    to be fetched more efficiently where required for rendering.
    """

    def __init__(
        self,
        *page_types: str,
        exclude_drafts: Optional[bool] = True,
        exclude_private: Optional[bool] = True,
        select_related: Optional[Sequence[str]] = None,
        prefetch_related: Optional[Sequence[Any]] = None,
        **kwargs,
    ):
        self.page_types = page_types
        self.select_related = select_related
        self.prefetch_related = prefetch_related
        self.exclude_drafts = exclude_drafts
        self.exclude_private = exclude_private
        child_block = APIPageChooserBlock(
            page_type=page_types,
            required_api_fields=["teaser_image"],
        )
        super().__init__(child_block, **kwargs)

    @cached_property
    def page_type_classes(self) -> Sequence[PageBase]:
        return [resolve_model_string(pt) for pt in self.page_types]

    def get_base_queryset(self) -> PageQuerySet:
        qs = Page.objects.all().specific()
        if self.page_type_classes:
            if len(self.page_type_classes) == 1:
                qs = self.page_type_classes[0].objects.all()
            else:
                qs = qs.type(*self.page_type_classes)
        if self.exclude_drafts:
            qs = qs.live()
        if self.exclude_private:
            qs = qs.public()
        if self.select_related:
            qs = qs.select_related(*self.select_related)
        if self.prefetch_related:
            qs = qs.prefetch_related(*self.prefetch_related)
        return qs

    def bulk_to_python(self, values) -> Sequence[ListValue]:
        return_value = []
        for block_value in values:
            return_value.append(self.to_python(block_value))
        return return_value

    def to_python(self, value) -> ListValue:
        # get a list of the child block values; this will be the 'value' item of the dict if the list item
        # is in the new block format, or the list item itself if in the old format
        raw_values = [
            item["value"] if self._item_is_in_block_format(item) else item
            for item in value
        ]
        # fetch pages to match these values
        pages_by_id = self.get_base_queryset().filter(id__in=raw_values).in_bulk()

        # assemble return value (a ListValue), only including items for which
        # a suitable page was found.
        bound_blocks = []
        for i, item in enumerate(value):
            if self._item_is_in_block_format(item):
                list_item_id = item["id"]
            else:
                list_item_id = None
            page_obj = pages_by_id.get(raw_values[i])
            if page_obj:
                bound_blocks.append(
                    ListValue.ListChild(self.child_block, page_obj, id=list_item_id)
                )
        return ListValue(self, bound_blocks=bound_blocks)

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        # The following options are 'rendering preferences' and should be
        # updatable without requiring a migration
        for key in (
            "exclude_drafts",
            "exclude_private",
            "select_related",
            "prefetch_related",
        ):
            kwargs.pop(key, None)
        return path, args, kwargs
