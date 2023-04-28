from django.test import TestCase

from ..models import ArticleTag


class TestArticleTagClean(TestCase):
    def test_clean_preserves_existing_skos_ids(self):
        tag = ArticleTag(name="Test", slug="test", skos_id="Preserve_Me")
        tag.clean()
        self.assertEqual(tag.skos_id, "Preserve_Me")

    def test_clean_does_not_generate_skos_id_when_no_name_specified(self):
        tag = ArticleTag(slug="test")
        tag.clean()
        self.assertEqual(tag.skos_id, "")

    def test_clean_generates_skos_id_from_name_with_no_conflicts(self):
        tag = ArticleTag(name="Test", slug="test")
        tag.clean()
        self.assertEqual(tag.skos_id, "Test")

    def test_clean_generates_skos_id_from_name_with_conflicts(self):
        ArticleTag.objects.create(name="Test", slug="test", skos_id="Test")
        ArticleTag.objects.create(name="Test 2", slug="test-2", skos_id="Test_2")

        tag = ArticleTag(name="Test", slug="test-3")
        tag.clean()
        self.assertEqual(tag.skos_id, "Test_3")
