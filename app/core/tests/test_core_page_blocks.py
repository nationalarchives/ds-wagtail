from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.core.blocks.lists import PeopleListingBlock
from app.core.blocks.page_chooser import APIPageChooserBlock
from app.core.blocks.promoted_links import FeaturedPageBlock
from app.core.serializers import DefaultPageSerializer
from django.test import SimpleTestCase


class APIPageChooserBlockTests(SimpleTestCase):
    @patch("app.core.blocks.page_chooser.get_api_data")
    def test_get_api_representation_passes_required_api_fields(self, mock_get_api_data):
        page = object()
        mock_get_api_data.return_value = {"teaser_image": {"id": 1}}
        block = APIPageChooserBlock(required_api_fields=["teaser_image"])

        representation = block.get_api_representation(page)

        self.assertEqual(representation, {"teaser_image": {"id": 1}})
        mock_get_api_data.assert_called_once_with(
            object=page,
            required_api_fields=["teaser_image"],
        )


class PeopleListingBlockTests(SimpleTestCase):
    def test_get_api_representation_returns_empty_without_role(self):
        block = PeopleListingBlock()

        representation = block.get_api_representation({"role": None})

        self.assertEqual(representation, {})

    def test_get_api_representation_returns_empty_when_role_has_no_people(self):
        person_roles = Mock()
        person_roles.all.return_value.order_by.return_value = []
        role = SimpleNamespace(name="Author", person_roles=person_roles)
        block = PeopleListingBlock()

        representation = block.get_api_representation({"role": role})

        self.assertEqual(representation, {})

    @patch.object(DefaultPageSerializer, "to_representation")
    def test_get_api_representation_serializes_people_for_role(
        self, mock_to_representation
    ):
        person_page = object()
        mock_to_representation.return_value = {"id": 12, "title": "Ada Lovelace"}
        ordered_people = [
            SimpleNamespace(person=person_page),
            SimpleNamespace(person=None),
        ]
        person_roles = Mock()
        person_roles.all.return_value.order_by.return_value = ordered_people
        role = SimpleNamespace(name="Author", person_roles=person_roles)
        block = PeopleListingBlock()

        representation = block.get_api_representation({"role": role})

        self.assertEqual(representation["role"], "Author")
        self.assertEqual(
            representation["people"],
            [{"id": 12, "title": "Ada Lovelace"}, None],
        )
        mock_to_representation.assert_called_once_with(person_page)


class FeaturedPageBlockTests(SimpleTestCase):
    @patch("app.core.blocks.page_chooser.get_api_data")
    def test_get_api_representation_overrides_page_teaser_text(self, mock_get_api_data):
        page = object()
        mock_get_api_data.return_value = {
            "title": "Feature",
            "teaser_text": "Original teaser",
        }
        block = FeaturedPageBlock()

        representation = block.get_api_representation(
            {"page": page, "teaser_text": "Override teaser"}
        )

        self.assertEqual(representation["page"]["teaser_text"], "Override teaser")
        self.assertNotIn("teaser_text", representation)
        mock_get_api_data.assert_called_once_with(
            object=page,
            required_api_fields=[],
        )

    @patch("app.core.blocks.page_chooser.get_api_data")
    def test_get_api_representation_without_teaser_override_keeps_original(
        self, mock_get_api_data
    ):
        page = object()
        mock_get_api_data.return_value = {
            "title": "Feature",
            "teaser_text": "Original teaser",
        }
        block = FeaturedPageBlock()

        representation = block.get_api_representation({"page": page, "teaser_text": ""})

        self.assertEqual(representation["page"]["teaser_text"], "Original teaser")
        self.assertNotIn("teaser_text", representation)
        mock_get_api_data.assert_called_once_with(
            object=page,
            required_api_fields=[],
        )
