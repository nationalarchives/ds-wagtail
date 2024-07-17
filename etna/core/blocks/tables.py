from wagtail import blocks
from wagtail.contrib.table_block.blocks import TableBlock


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
