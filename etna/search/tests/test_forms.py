from django.test import SimpleTestCase

from ..forms import CatalogueSearchForm


class CatalogueSearchFormTest(SimpleTestCase):
    def test_valid_date_range_values(self):
        """tests inputs accross both date fields with various input formats for form validity"""

        for from_field_name, to_field_name in (
            ("opening_start_date", "opening_end_date"),
            ("covering_date_from", "covering_date_to"),
        ):
            for label, form_data in (
                (
                    "start date supplied without end date",
                    {
                        f"{from_field_name}_0": "31",
                        f"{from_field_name}_1": "12",
                        f"{from_field_name}_2": "1999",
                    },
                ),
                (
                    "end date supplied without start date",
                    {
                        f"{to_field_name}_0": "01",
                        f"{to_field_name}_1": "01",
                        f"{to_field_name}_2": "2000",
                    },
                ),
                (
                    "different start date and end dates supplied in correct range order",
                    {
                        f"{from_field_name}_0": "31",
                        f"{from_field_name}_1": "12",
                        f"{from_field_name}_2": "1999",
                        f"{to_field_name}_0": "01",
                        f"{to_field_name}_1": "01",
                        f"{to_field_name}_2": "2000",
                    },
                ),
                (
                    "equal start and end dates supplied",
                    {
                        f"{from_field_name}_0": "31",
                        f"{from_field_name}_1": "12",
                        f"{from_field_name}_2": "1999",
                        f"{to_field_name}_0": "31",
                        f"{to_field_name}_1": "12",
                        f"{to_field_name}_2": "1999",
                    },
                ),
            ):
                with self.subTest(label):
                    form = CatalogueSearchForm(data={"group": "tna", **form_data})
                    self.assertTrue(form.is_valid(), label)

    def test_invalid_date_range_values(self):
        for from_field_name, to_field_name in (
            # ("opening_start_date", "opening_end_date"), # TODO: Keep, not in scope for Ohos-Etna at this time
            ("covering_date_from", "covering_date_to"),
        ):
            for label, form_data in (
                (
                    "start date and end date supplied in incorrect range order",
                    {
                        f"{from_field_name}_0": "01",
                        f"{from_field_name}_1": "01",
                        f"{from_field_name}_2": "2000",
                        f"{to_field_name}_0": "31",
                        f"{to_field_name}_1": "12",
                        f"{to_field_name}_2": "1999",
                    },
                ),
                (
                    "only year values supplied for both dates",
                    {
                        f"{from_field_name}_2": "2000",
                        f"{to_field_name}_2": "1999",
                    },
                ),
                (
                    "only month and year values supplied for both dates",
                    {
                        f"{from_field_name}_1": "01",
                        f"{from_field_name}_2": "2000",
                        f"{to_field_name}_1": "12",
                        f"{to_field_name}_2": "1999",
                    },
                ),
            ):
                with self.subTest(label):
                    form = CatalogueSearchForm(data={"group": "tna", **form_data})
                    self.assertFalse(form.is_valid(), label)
                    self.assertEqual(
                        form.errors.get(from_field_name, None),
                        ["This date must be earlier than or equal to the 'to' date."],
                    )
