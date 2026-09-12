import json
from collections import defaultdict
from collections.abc import Iterable, Mapping

from django.apps import apps
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.models import Page


def snake_to_sentence_case(text):
    """Convert snake_case to Sentence case (e.g., 'my_block_name' -> 'My block name')."""
    words = text.split("_")
    return " ".join(words).capitalize()


def iter_block_types(stream_data):
    """Yield all block types from StreamField values, including nested sub-blocks."""

    def looks_like_block_dict(value):
        return (
            isinstance(value, Mapping)
            and "type" in value
            and ("value" in value or "id" in value or len(value) == 1)
        )

    seen = set()

    def walk(value):
        if value is None:
            return

        if isinstance(value, str):
            stripped = value.strip()
            if not stripped or stripped[0] not in "[{":
                return
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                return

        # Prevent re-walking the same nested container.
        if isinstance(value, (Mapping, Iterable)) and not isinstance(
            value, (str, bytes)
        ):
            object_id = id(value)
            if object_id in seen:
                return
            seen.add(object_id)

        block_type = getattr(value, "block_type", None)
        if block_type:
            yield block_type
            yield from walk(getattr(value, "value", None))
            return

        if looks_like_block_dict(value):
            yield value["type"]
            if "value" in value:
                yield from walk(value["value"])
            return

        if isinstance(value, Mapping):
            for child_value in value.values():
                yield from walk(child_value)
            return

        if hasattr(value, "items") and not isinstance(value, dict):
            for _, child_value in value.items():
                yield from walk(child_value)
            return

        if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            for child_value in value:
                yield from walk(child_value)

    yield from walk(stream_data)


def get_streamfield_names():
    """Return all StreamField names defined on Wagtail Page subclasses."""
    field_names = set()
    page_models = [
        model
        for model in apps.get_models()
        if issubclass(model, Page) and model != Page
    ]

    for model in page_models:
        for field in model._meta.get_fields():
            if isinstance(field, StreamField):
                field_names.add(field.name)

    return sorted(field_names)


def get_block_type_names():
    """Return all StreamBlock child names defined on Wagtail Page StreamFields."""
    block_type_names = set()
    page_models = [
        model
        for model in apps.get_models()
        if issubclass(model, Page) and model != Page
    ]

    def walk_declared_block_types(block):
        if isinstance(block, blocks.StreamBlock):
            for child_name, child_block in block.child_blocks.items():
                block_type_names.add(child_name)
                walk_declared_block_types(child_block)
            return

        if isinstance(block, blocks.StructBlock):
            for child_block in block.child_blocks.values():
                walk_declared_block_types(child_block)
            return

        if isinstance(block, blocks.ListBlock):
            walk_declared_block_types(block.child_block)

    for model in page_models:
        for field in model._meta.get_fields():
            if isinstance(field, StreamField):
                walk_declared_block_types(field.stream_block)

    return sorted(block_type_names)


def get_block_type_labels():
    """Return a dict of block_type_name -> human-readable label from block Meta.label."""
    labels = {}
    page_models = [
        model
        for model in apps.get_models()
        if issubclass(model, Page) and model != Page
    ]

    def walk_and_collect_labels(block):
        if isinstance(block, blocks.StreamBlock):
            for child_name, child_block in block.child_blocks.items():
                label = getattr(child_block.meta, "label", None)
                if label:
                    labels[child_name] = str(label)
                walk_and_collect_labels(child_block)
            return

        if isinstance(block, blocks.StructBlock):
            for child_block in block.child_blocks.values():
                walk_and_collect_labels(child_block)
            return

        if isinstance(block, blocks.ListBlock):
            walk_and_collect_labels(block.child_block)

    for model in page_models:
        for field in model._meta.get_fields():
            if isinstance(field, StreamField):
                walk_and_collect_labels(field.stream_block)

    return labels


def get_block_usage(
    specific_field=None,
    specific_block=None,
    verbose=False,
    log=None,
    error_log=None,
):
    """Count StreamField block usage across all Wagtail Page subclasses."""
    block_usage = defaultdict(lambda: defaultdict(int))

    page_models = [
        model
        for model in apps.get_models()
        if issubclass(model, Page) and model != Page
    ]

    if verbose and callable(log):
        log(f"Found {len(page_models)} Page subclasses")

    for model in page_models:
        if verbose and callable(log):
            log(f"\nChecking {model.__name__}...")

        stream_fields = []
        for field in model._meta.get_fields():
            if isinstance(field, StreamField):
                stream_fields.append(field)
                if verbose and callable(log):
                    log(f"  Found StreamField: {field.name}")

        for field in stream_fields:
            if specific_field and field.name != specific_field:
                continue

            try:
                queryset = model.objects.all().values_list(field.name, flat=True)

                for stream_data in queryset:
                    if not stream_data:
                        continue

                    for block_type in iter_block_types(stream_data):
                        if specific_block and block_type != specific_block:
                            continue
                        field_key = f"{model.__name__}.{field.name}"
                        block_usage[field_key][block_type] += 1

            except Exception as exc:  # noqa: BLE001
                if callable(error_log):
                    error_log(model, field, exc)

    return {field_name: dict(blocks) for field_name, blocks in block_usage.items()}


def get_block_usage_with_pages(
    specific_field=None,
    specific_block=None,
    verbose=False,
    log=None,
    error_log=None,
):
    """Count StreamField block usage and return per-page details for each block type."""
    block_usage = defaultdict(lambda: defaultdict(lambda: {"count": 0, "pages": []}))

    page_models = [
        model
        for model in apps.get_models()
        if issubclass(model, Page) and model != Page
    ]

    if verbose and callable(log):
        log(f"Found {len(page_models)} Page subclasses")

    for model in page_models:
        if verbose and callable(log):
            log(f"\nChecking {model.__name__}...")

        stream_fields = []
        for field in model._meta.get_fields():
            if isinstance(field, StreamField):
                stream_fields.append(field)
                if verbose and callable(log):
                    log(f"  Found StreamField: {field.name}")

        for field in stream_fields:
            if specific_field and field.name != specific_field:
                continue

            try:
                queryset = model.objects.all().values_list("pk", "title", field.name)

                for page_id, page_title, stream_data in queryset:
                    if not stream_data:
                        continue

                    page_block_counts = defaultdict(int)
                    for block_type in iter_block_types(stream_data):
                        page_block_counts[block_type] += 1

                    if not page_block_counts:
                        continue

                    field_key = f"{model.__name__}.{field.name}"
                    for block_type, page_count in page_block_counts.items():
                        if specific_block and block_type != specific_block:
                            continue
                        block_entry = block_usage[field_key][block_type]
                        block_entry["count"] += page_count
                        block_entry["pages"].append(
                            {
                                "id": page_id,
                                "title": page_title,
                                "page_type": model.__name__,
                                "occurrences": page_count,
                            }
                        )

            except Exception as exc:  # noqa: BLE001
                if callable(error_log):
                    error_log(model, field, exc)

    return {
        field_name: {
            block_type: {
                "count": block_data["count"],
                "pages": sorted(
                    block_data["pages"],
                    key=lambda page: (
                        -page["occurrences"],
                        page["title"].lower(),
                        page["id"],
                    ),
                ),
            }
            for block_type, block_data in blocks.items()
        }
        for field_name, blocks in block_usage.items()
    }
