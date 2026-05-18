from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from wagtail.models import GroupPagePermission, Site

from app.articles.factories import ArticleIndexPageFactory, ArticlePageFactory
from app.core.admin_views import (
    TREE_EXPLORER_CACHE_NAMESPACE,
    _get_tree_cache_key,
    get_tree_nodes,
    invalidate_tree_explorer_cache,
)


class TreeExplorerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_page = Site.objects.get(is_default_site=True).root_page

        cls.allowed_index = ArticleIndexPageFactory(
            parent=cls.root_page,
            title="Allowed index",
        )
        cls.disallowed_index = ArticleIndexPageFactory(
            parent=cls.root_page,
            title="Disallowed index",
        )

        cls.allowed_child = ArticlePageFactory(
            parent=cls.allowed_index,
            title="Allowed child",
        )
        cls.disallowed_child = ArticlePageFactory(
            parent=cls.disallowed_index,
            title="Disallowed child",
        )

        user_model = get_user_model()

        cls.editor = user_model.objects.create_user(
            username="tree-editor",
            password="password123",
            is_staff=True,
        )

        cls.superuser = user_model.objects.create_superuser(
            username="tree-superuser",
            email="tree-superuser@example.com",
            password="password123",
        )
        cls.other_superuser = user_model.objects.create_superuser(
            username="tree-superuser-2",
            email="tree-superuser-2@example.com",
            password="password123",
        )

        access_admin_permission = Permission.objects.get(codename="access_admin")
        cls.editor.user_permissions.add(access_admin_permission)

        editors_group = Group.objects.create(name="Tree editors")
        cls.editor.groups.add(editors_group)

        GroupPagePermission.objects.create(
            group=editors_group,
            page=cls.allowed_index,
            permission_type="change",
        )

    def setUp(self):
        cache.clear()

    def _flatten_page_ids(self, nodes):
        ids = []
        stack = list(nodes)

        while stack:
            node = stack.pop()
            ids.append(node["page_id"])
            stack.extend(node["children"])

        return ids

    def test_tree_view_only_shows_explorable_pages_for_user(self):
        self.client.force_login(self.editor)

        response = self.client.get(reverse("tree_explorer"))

        self.assertEqual(response.status_code, 200)

        page_ids = self._flatten_page_ids(response.context["tree_nodes"])

        self.assertIn(self.allowed_index.id, page_ids)
        self.assertIn(self.allowed_child.id, page_ids)
        self.assertNotIn(self.disallowed_index.id, page_ids)
        self.assertNotIn(self.disallowed_child.id, page_ids)

    def test_get_tree_nodes_populates_cache(self):
        cache_key = _get_tree_cache_key(self.superuser)

        self.assertIsNone(cache.get(cache_key))

        get_tree_nodes(self.superuser)

        self.assertIsNotNone(cache.get(cache_key))

    def test_invalidate_tree_explorer_cache_clears_cached_keys_when_supported(self):
        key_one = _get_tree_cache_key(self.superuser)
        key_two = _get_tree_cache_key(self.other_superuser)

        get_tree_nodes(self.superuser)
        get_tree_nodes(self.other_superuser)

        self.assertIsNotNone(cache.get(key_one))
        self.assertIsNotNone(cache.get(key_two))

        pattern = f"{TREE_EXPLORER_CACHE_NAMESPACE}:u*"

        def fake_delete_pattern(value):
            self.assertEqual(value, pattern)
            cache.delete(key_one)
            cache.delete(key_two)

        with patch.object(
            cache,
            "delete_pattern",
            side_effect=fake_delete_pattern,
            create=True,
        ) as mocked_delete_pattern:
            invalidate_tree_explorer_cache()

        mocked_delete_pattern.assert_called_once_with(pattern)
        self.assertIsNone(cache.get(key_one))
        self.assertIsNone(cache.get(key_two))
