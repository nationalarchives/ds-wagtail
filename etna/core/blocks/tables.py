from wagtail import blocks
from wagtail.contrib.table_block.blocks import TableBlock


class ContentTableBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=100,
        help_text="Title of the table",
        label="Title",
        required=False,
    )
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
