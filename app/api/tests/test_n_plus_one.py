from unittest.mock import patch

from django.db import connection
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from wagtail.models import Page, PageViewRestriction, Site

from app.api.filters import AliasFilter
from app.api.models import APIToken
from app.articles.models import ArticlePage, FocusedArticlePage
from app.blog.models import BlogPage, BlogPostPage
from app.core.blocks.lists import PeopleListingBlock
from app.core.serializers.pages import DefaultPageSerializer, prefetch_page_relations
from app.images.models import CustomImage
from app.people.models import (
    PeopleIndexPage,
    PersonPage,
    PersonRole,
    PersonRoleSelection,
)


class NPlusOneTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root = Site.objects.get(is_default_site=True).root_page
        cls.token = APIToken.objects.create(name="n-plus-one-test")

    def test_listing_loads_teaser_images_in_bulk(self):
        image = CustomImage.objects.create(
            title="Placeholder", file="placeholder.jpg", width=1, height=1
        )
        pages = []
        for i, model in enumerate(
            [FocusedArticlePage, FocusedArticlePage, ArticlePage]
        ):
            pages.append(
                self.root.add_child(
                    instance=model(
                        title=f"Image page {i}",
                        intro="<p>Intro</p>",
                        teaser_text="Teaser",
                        teaser_image=image,
                    )
                )
            )

        with (
            patch(
                "app.core.serializers.images.ImageSerializer.to_representation",
                return_value=None,
            ),
            CaptureQueriesContext(connection) as queries,
        ):
            response = self.client.get(
                "/api/v2/pages/",
                {"child_of": self.root.pk, "order": "title", "include_aliases": "1"},
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.json()["items"]],
            [page.pk for page in pages],
        )
        image_queries = [
            query["sql"]
            for query in queries
            if 'FROM "images_customimage"' in query["sql"]
        ]
        self.assertEqual(len(image_queries), 1)

    def test_prefetch_skips_base_pages_and_excludes_unselected_images(self):
        image = CustomImage.objects.create(
            title="Selected", file="selected.jpg", width=1, height=1
        )
        unused_image = CustomImage.objects.create(
            title="Not selected", file="not-selected.jpg", width=1, height=1
        )
        self.root.add_child(instance=Page(title="Plain"))
        selected = self.root.add_child(
            instance=FocusedArticlePage(
                title="Selected",
                intro="Intro",
                teaser_text="Teaser",
                teaser_image=image,
            )
        )
        self.root.add_child(
            instance=FocusedArticlePage(
                title="Unselected",
                intro="Intro",
                teaser_text="Teaser",
                teaser_image=unused_image,
            )
        )
        pages = list(Page.objects.child_of(self.root).order_by("title")[:2].specific())
        image_params = []

        def capture_image_query(execute, sql, params, many, context):
            if 'FROM "images_customimage"' in sql:
                image_params.extend(params)
            return execute(sql, params, many, context)

        with connection.execute_wrapper(capture_image_query):
            prefetch_page_relations(pages)
            self.assertEqual(pages[1].teaser_image.pk, selected.teaser_image_id)

        self.assertEqual(image_params, [image.pk])

    def test_person_role_tags_fetch_roles_in_bulk(self):
        person = self.root.add_child(
            instance=PersonPage(
                title="Person",
                first_name="First",
                last_name="Last",
                role="Author",
                summary="Summary",
                teaser_text="Teaser",
            )
        )
        for name, display in [("Second", True), ("First", True), ("Hidden", False)]:
            role = PersonRole.objects.create(
                name=name, slug=name.lower(), display_on_card=display
            )
            PersonRoleSelection.objects.create(person=person, role=role)

        with CaptureQueriesContext(connection) as queries:
            result = PersonPage.objects.get(pk=person.pk).role_tags

        self.assertEqual(
            result,
            [{"slug": "first", "name": "First"}, {"slug": "second", "name": "Second"}],
        )
        role_queries = [
            query["sql"]
            for query in queries
            if 'FROM "people_personrole"' in query["sql"]
        ]
        self.assertEqual(len(role_queries), 1)

    def test_unsaved_person_role_tags_use_in_memory_roles(self):
        role = PersonRole.objects.create(
            name="Author", slug="author", display_on_card=True
        )
        person = PersonPage(title="Draft")
        person.roles.add(PersonRoleSelection(role=role))

        with self.assertNumQueries(0):
            self.assertEqual(person.role_tags, [{"slug": "author", "name": "Author"}])

    def test_people_index_batches_person_roles(self):
        index = self.root.add_child(
            instance=PeopleIndexPage(title="People", teaser_text="Teaser")
        )
        role = PersonRole.objects.create(
            name="Author", slug="author", display_on_card=True
        )
        for i in range(3):
            person = index.add_child(
                instance=PersonPage(
                    title=f"Person {i}",
                    first_name=f"First {i}",
                    last_name="Last",
                    role="Author",
                    summary="Summary",
                    teaser_text="Teaser",
                )
            )
            PersonRoleSelection.objects.create(person=person, role=role)

        with CaptureQueriesContext(connection) as queries:
            data = DefaultPageSerializer(index.people_pages, many=True).data

        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["role_tags"], [{"slug": "author", "name": "Author"}])
        role_queries = [
            query["sql"]
            for query in queries
            if 'FROM "people_personrole"' in query["sql"]
        ]
        self.assertEqual(len(role_queries), 1)

    def test_pages_endpoint_batches_person_roles(self):
        role = PersonRole.objects.create(
            name="Author", slug="author", display_on_card=True
        )
        for i in range(3):
            person = self.root.add_child(
                instance=PersonPage(
                    title=f"Person {i}",
                    first_name=f"First {i}",
                    last_name="Last",
                    role="Author",
                    summary="Summary",
                    teaser_text="Teaser",
                )
            )
            PersonRoleSelection.objects.create(person=person, role=role)

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                "/api/v2/pages/",
                {"child_of": self.root.pk, "include_aliases": "1"},
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 3)
        role_queries = [
            query["sql"]
            for query in queries
            if 'FROM "people_personrole"' in query["sql"]
        ]
        self.assertEqual(len(role_queries), 1)

    def test_people_listing_loads_people_and_roles_in_bulk(self):
        role = PersonRole.objects.create(
            name="Authors", slug="authors", display_on_card=True
        )
        pages = []
        for i in range(3):
            page = self.root.add_child(
                instance=PersonPage(
                    title=f"Person {i}",
                    first_name=f"First {i}",
                    last_name="Last",
                    role="Author",
                    summary="Summary",
                    teaser_text="Teaser",
                )
            )
            PersonRoleSelection.objects.create(person=page, role=role, weighting=3 - i)
            pages.append(page)

        with CaptureQueriesContext(connection) as queries:
            result = PeopleListingBlock().get_api_representation({"role": role})

        self.assertEqual(
            [item["id"] for item in result["people"]], [p.pk for p in pages]
        )
        person_queries = [
            query["sql"]
            for query in queries
            if 'FROM "people_personpage"' in query["sql"]
        ]
        self.assertEqual(person_queries, [])
        role_selection_queries = [
            query["sql"]
            for query in queries
            if 'FROM "people_personroleselection"' in query["sql"]
        ]
        self.assertEqual(len(role_selection_queries), 2)

    def test_top_blogs_counts_descendant_posts_without_per_blog_queries(self):
        blog_a = self.root.add_child(
            instance=BlogPage(title="Blog A", intro="Intro", teaser_text="Teaser")
        )
        blog_b = self.root.add_child(
            instance=BlogPage(title="Blog B", intro="Intro", teaser_text="Teaser")
        )
        child = blog_a.add_child(
            instance=BlogPage(title="Child blog", intro="Intro", teaser_text="Teaser")
        )
        for parent, title, live in [
            (blog_a, "Direct post", True),
            (child, "Nested post", True),
            (blog_a, "Draft post", False),
            (blog_a, "Private post", True),
        ]:
            post = parent.add_child(
                instance=BlogPostPage(
                    title=title,
                    intro="Intro",
                    teaser_text="Teaser",
                    published_date=timezone.now(),
                    live=live,
                )
            )
            if title == "Private post":
                PageViewRestriction.objects.create(
                    page=post,
                    restriction_type=PageViewRestriction.PASSWORD,
                    password="test",
                )

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                "/api/v2/blogs/top/",
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [(item["id"], item["posts"]) for item in response.json()],
            [(blog_a.pk, 2), (blog_b.pk, 0)],
        )
        count_queries = [
            query["sql"]
            for query in queries
            if query["sql"].lstrip().startswith("SELECT COUNT(")
            and "blog_blogpostpage" in query["sql"]
        ]
        self.assertEqual(count_queries, [])

    def test_alias_filter_batches_alias_group_lookups(self):
        original = self.root.add_child(instance=Page(title="Original"))
        other = self.root.add_child(instance=Page(title="Other"))
        folder = self.root.add_child(instance=Page(title="Folder"))
        deeper = folder.add_child(instance=Page(title="Deeper"))
        shallow_alias = folder.add_child(
            instance=Page(title="Shallow", alias_of=original)
        )
        deep_alias = deeper.add_child(instance=Page(title="Deep", alias_of=original))
        other_alias = folder.add_child(
            instance=Page(title="Other alias", alias_of=other)
        )
        queryset = Page.objects.filter(
            pk__in=[shallow_alias.pk, deep_alias.pk, other.pk, other_alias.pk]
        )

        with CaptureQueriesContext(connection) as queries:
            result = list(
                AliasFilter().filter_queryset(RequestFactory().get("/"), queryset, None)
            )

        self.assertEqual({page.pk for page in result}, {shallow_alias.pk, other.pk})
        self.assertLessEqual(len(queries), 3)

    def test_alias_filter_preserves_chains_and_include_aliases(self):
        original = self.root.add_child(instance=Page(title="Original"))
        alias = self.root.add_child(instance=Page(title="Alias", alias_of=original))
        alias_child = self.root.add_child(instance=Page(title="Chain", alias_of=alias))
        queryset = Page.objects.filter(pk__in=[original.pk, alias.pk, alias_child.pk])

        filtered = AliasFilter().filter_queryset(
            RequestFactory().get("/"), queryset, None
        )
        self.assertEqual(list(filtered.values_list("pk", flat=True)), [original.pk])

        included = AliasFilter().filter_queryset(
            RequestFactory().get("/", {"include_aliases": "1"}), queryset, None
        )
        self.assertEqual(
            set(included.values_list("pk", flat=True)),
            set(queryset.values_list("pk", flat=True)),
        )
