from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.encoding import force_str
from wagtail.admin.auth import require_admin_access
from wagtail.models import Page
from wagtail.permission_policies.pages import PagePermissionPolicy

from app.core.block_usage import (
    get_block_type_labels,
    get_block_type_names,
    get_block_usage_with_pages,
    snake_to_sentence_case,
)

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

    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        model = None

    if model is None:
        label = model_name.replace("_", " ")
    elif hasattr(model, "get_verbose_name"):
        label = model.get_verbose_name()
    else:
        label = model._meta.verbose_name

    label = force_str(label)
    cached_labels[key] = label
    return label


def _build_tree_nodes(user):
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
            url_parts = page.get_url_parts()
            if url_parts is not None:
                _, root_url, page_path = url_parts
                if root_url and page_path:
                    live_urls[page.id] = f"{root_url}{page_path}"

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


def get_tree_nodes(user):
    cache_key = _get_tree_cache_key(user)
    tree_nodes = cache.get(cache_key)
    if tree_nodes is not None:
        return tree_nodes

    tree_nodes = _build_tree_nodes(user)
    cache.set(cache_key, tree_nodes, timeout=TREE_EXPLORER_CACHE_TIMEOUT)
    return tree_nodes


@require_admin_access
def tree_explorer_view(request):
    """Render a full page tree with in-place accordion expansion."""
    tree_nodes = get_tree_nodes(request.user)
    return render(
        request,
        "wagtailadmin/pages/tree_explorer.html",
        {
            "tree_nodes": tree_nodes,
        },
    )


@require_admin_access
def block_usage_report_view(request):
    """Render a block usage report for all StreamFields in the site."""
    selected_block = request.GET.get("block") or ""
    block_usage = get_block_usage_with_pages(specific_block=selected_block or None)
    block_labels = get_block_type_labels()
    block_type_names = get_block_type_names()

    rows = []
    total_blocks = 0
    for field_name in sorted(block_usage.keys()):
        blocks = block_usage[field_name]
        sorted_blocks = sorted(
            blocks.items(), key=lambda item: item[1]["count"], reverse=True
        )
        field_total = sum(block["count"] for block in blocks.values())
        total_blocks += field_total
        rows.append(
            {
                "field_name": field_name,
                "field_total": field_total,
                "blocks": [
                    {
                        "block_type": block_type,
                        "block_label": block_labels.get(
                            block_type, snake_to_sentence_case(block_type)
                        ),
                        "count": block_data["count"],
                        "pages": block_data["pages"],
                    }
                    for block_type, block_data in sorted_blocks
                ],
            }
        )

    # Build block_type_options with both name and label for dropdown
    block_type_options = [
        {
            "value": block_type,
            "label": block_labels.get(block_type, snake_to_sentence_case(block_type)),
        }
        for block_type in block_type_names
    ]

    # Paginate rows
    paginator = Paginator(rows, 5)  # 5 fields per page
    page_num = request.GET.get("page", 1)
    try:
        page_obj = paginator.page(page_num)
    except Exception:
        page_obj = paginator.page(1)

    return render(
        request,
        "wagtailadmin/reports/block_usage.html",
        {
            "page_obj": page_obj,
            "total_blocks": total_blocks,
            "block_type_options": block_type_options,
            "selected_block": selected_block,
        },
    )
