from django.core.exceptions import ValidationError
from wagtail import blocks
from wagtail.contrib.table_block.blocks import TableBlock as WagtailTableBlock


class TableBlock(WagtailTableBlock):
    def clean(self, value):
        value = super().clean(value)

        if value and not value.get("table_caption", "").strip():
            raise ValidationError("You must provide a table caption.")

        return value


class ContentTableBlock(blocks.StructBlock):
    table = TableBlock(
        table_options={
            "contextMenu": [
                "row_above",
                "row_below",
                "---------",
                "col_left",
                "col_right",
                "---------",
                "remove_row",
                "remove_col",
                "---------",
                "undo",
                "redo",
                "---------",
                "alignment",
            ]
        }
    )

    class Meta:
        icon = "table"
        label = "Table"
        group = "Structured and collapsible content"
