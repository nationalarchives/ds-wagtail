from django.shortcuts import render
from wagtail.admin.auth import require_admin_access
from wagtail.models import Page


@require_admin_access
def tree_explorer_view(request):
    """Render a full page tree with in-place accordion expansion."""
    pages = (
        Page.objects.select_related("content_type")
        .only(
            "id",
            "title",
            "path",
            "depth",
            "live",
            "has_unpublished_changes",
            "content_type",
        )
        .order_by("path")
    )

    nodes_by_path = {}
    root_nodes = []

    for page in pages:
        node = {
            "page": page,
            "children": [],
        }
        nodes_by_path[page.path] = node

        if page.depth == 1:
            continue

        if page.depth == 2:
            root_nodes.append(node)
            continue

        parent_path = page.path[: -page.steplen]
        parent = nodes_by_path.get(parent_path)

        if parent is None:
            root_nodes.append(node)
            continue

        parent["children"].append(node)

    return render(
        request,
        "wagtailadmin/pages/tree_explorer.html",
        {
            "tree_nodes": root_nodes,
        },
    )
