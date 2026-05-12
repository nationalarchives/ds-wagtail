from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.utils.encoding import force_str
from time import perf_counter
from wagtail.admin.auth import require_admin_access
from wagtail.models import Page


TREE_EXPLORER_CACHE_KEY = "core:wagtail:tree_explorer:v2"
TREE_EXPLORER_CACHE_TIMEOUT = getattr(settings, "TREE_EXPLORER_CACHE_TIMEOUT", 300)


def invalidate_tree_explorer_cache():
    cache.delete(TREE_EXPLORER_CACHE_KEY)


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


def _build_tree_nodes():
    rows = (
        Page.objects.select_related("content_type")
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

    nodes_by_path = {}
    root_nodes = []
    cached_labels = {}

    for row in rows:
        node = {
            "page_id": row["id"],
            "title": row["title"],
            "verbose_name": _get_page_verbose_name(
                row["content_type__app_label"],
                row["content_type__model"],
                cached_labels,
            ),
            "live": row["live"],
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

    return root_nodes


def get_tree_nodes():
    start_time = perf_counter()
    tree_nodes = cache.get(TREE_EXPLORER_CACHE_KEY)
    if tree_nodes is not None:
        elapsed_ms = (perf_counter() - start_time) * 1000
        return tree_nodes, "hit", elapsed_ms

    tree_nodes = _build_tree_nodes()
    cache.set(TREE_EXPLORER_CACHE_KEY, tree_nodes, timeout=TREE_EXPLORER_CACHE_TIMEOUT)
    elapsed_ms = (perf_counter() - start_time) * 1000
    return tree_nodes, "miss", elapsed_ms


@require_admin_access
def tree_explorer_view(request):
    """Render a full page tree with in-place accordion expansion."""
    tree_nodes, cache_status, tree_data_time_ms = get_tree_nodes()
    response = render(
        request,
        "wagtailadmin/pages/tree_explorer.html",
        {
            "tree_nodes": tree_nodes,
            "tree_cache_status": cache_status,
            "tree_data_time_ms": tree_data_time_ms,
            "tree_cache_key": TREE_EXPLORER_CACHE_KEY,
        },
    )
    response["X-Tree-Explorer-Cache"] = cache_status
    response["X-Tree-Explorer-Data-Time-Ms"] = f"{tree_data_time_ms:.2f}"
    response["X-Tree-Explorer-Cache-Key"] = TREE_EXPLORER_CACHE_KEY
    return response
