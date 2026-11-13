from django.test import SimpleTestCase

from app.core.block_usage import iter_block_types


class FakeBlock:
    def __init__(self, block_type, value):
        self.block_type = block_type
        self.value = value


class IterBlockTypesTests(SimpleTestCase):
    def test_recurses_through_nested_dict_stream_shapes(self):
        stream_data = [
            {
                "type": "content_section",
                "value": {
                    "heading": "Section",
                    "content": [
                        {"type": "paragraph", "value": "Body"},
                        {
                            "type": "accordion",
                            "value": [
                                {
                                    "type": "details",
                                    "value": {
                                        "summary": "One",
                                        "content": [{"type": "image", "value": 123}],
                                    },
                                }
                            ],
                        },
                    ],
                },
            }
        ]

        block_types = list(iter_block_types(stream_data))

        self.assertEqual(
            block_types,
            ["content_section", "paragraph", "accordion", "details", "image"],
        )

    def test_recurses_through_stream_child_like_objects(self):
        stream_data = [
            FakeBlock(
                "content_section",
                {
                    "content": [
                        FakeBlock("paragraph", "Body"),
                        FakeBlock("image", {"id": 1}),
                    ]
                },
            )
        ]

        block_types = list(iter_block_types(stream_data))

        self.assertEqual(block_types, ["content_section", "paragraph", "image"])

    def test_ignores_plain_text_values(self):
        self.assertEqual(list(iter_block_types("not json")), [])
