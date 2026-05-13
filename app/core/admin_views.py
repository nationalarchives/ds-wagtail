from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.utils.encoding import force_str
from wagtail.admin.auth import require_admin_access
from wagtail.models import Page
from wagtail.permission_policies.pages import PagePermissionPolicy

TREE_EXPLORER_CACHE_NAMESPACE = "core:wagtail:tree_explorer"
TREE_EXPLORER_CACHE_TIMEOUT = getattr(settings, "TREE_EXPLORER_CACHE_TIMEOUT", 300)
PAGE_PERMISSION_POLICY = PagePermissionPolicy()


def invalidate_tree_explorer_cache(
    *args, **kwargs
):  # We don't need args/kwargs, but the signal handlers will pass them in, so we need to accept them as parameters.
    delete_pattern = getattr(cache, "delete_pattern", None)
    if callable(delete_pattern):
        delete_pattern(f"{TREE_EXPLORER_CACHE_NAMESPACE}:u*")


def _get_tree_cache_key(user):
    return f"{TREE_EXPLORER_CACHE_NAMESPACE}:u{user.pk}"


def _get_page_verbose_name(app_label, model_name, cached_labels):
    key = (app_label, model_name)
    if key in cached_labels:
        return cached_labels[key]

    model = apps.get_model(app_label, model_name)
    if model is None:
        label = model_name.replace("_", " ")
    elif hasattr(model, "get_verbose_name"):
        label = model.get_verbose_name()
    else:
        label = model._meta.verbose_name

    label = force_str(label)
    cached_labels[key] = label
    return label


def _build_tree_nodes(user, request):
    explorable_pages = PAGE_PERMISSION_POLICY.explorable_instances(user)
    pages = list(
        explorable_pages.select_related("content_type")
        .values(
            "id",
            "title",
            "path",
            "depth",
            "live",
            "content_type__app_label",
            "content_type__model",
        )
        .order_by("path")
    )

    live_urls = {}
    live_page_ids = [row["id"] for row in pages if row["live"]]
    if live_page_ids:
        for page in Page.objects.filter(id__in=live_page_ids).only("id", "url_path"):
            live_urls[page.id] = page.get_url(request=request)

    nodes_by_path = {}
    root_nodes = []
    cached_labels = {}

    for row in pages:
        node = {
            "page_id": row["id"],
            "title": row["title"],
            "verbose_name": _get_page_verbose_name(
                row["content_type__app_label"],
                row["content_type__model"],
                cached_labels,
            ),
            "live": row["live"],
            "live_url": live_urls.get(row["id"]),
            "child_count": 0,
            "children": [],
        }
        nodes_by_path[row["path"]] = node

        if row["depth"] == 1:
            continue

        if row["depth"] == 2:
            root_nodes.append(node)
            continue

        parent_path = row["path"][: -Page.steplen]
        parent = nodes_by_path.get(parent_path)

        if parent is None:
            root_nodes.append(node)
            continue

        parent["children"].append(node)
        parent["child_count"] += 1

    return root_nodes


def get_tree_nodes(user, request):
    cache_key = _get_tree_cache_key(user)
    tree_nodes = cache.get(cache_key)
    if tree_nodes is not None:
        return tree_nodes

    tree_nodes = _build_tree_nodes(user, request)
    cache.set(cache_key, tree_nodes, timeout=TREE_EXPLORER_CACHE_TIMEOUT)
    return tree_nodes


@require_admin_access
def tree_explorer_view(request):
    """Render a full page tree with in-place accordion expansion."""
    tree_nodes = get_tree_nodes(request.user, request)
    return render(
        request,
        "wagtailadmin/pages/tree_explorer.html",
        {
            "tree_nodes": tree_nodes,
        },
    )
