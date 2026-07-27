from django.test import SimpleTestCase

from app.core.blocks.lists import DescriptionListSettingsBlock


class DescriptionListSettingsBlockTests(SimpleTestCase):
    def test_empty_choice_values_are_serialized_as_none(self):
        block = DescriptionListSettingsBlock()
        value = block.to_python(
            {
                "style": "none",
                "column_balancing": "none",
                "stacked": False,
            }
        )

        self.assertEqual(
            block.get_api_representation(value),
            {
                "style": None,
                "column_balancing": None,
                "stacked": False,
            },
        )

    def test_non_empty_choice_values_are_preserved(self):
        block = DescriptionListSettingsBlock()
        value = block.to_python(
            {
                "style": "lined",
                "column_balancing": "even",
                "stacked": True,
            }
        )

        self.assertEqual(
            block.get_api_representation(value),
            {
                "style": "lined",
                "column_balancing": "even",
                "stacked": True,
            },
        )
