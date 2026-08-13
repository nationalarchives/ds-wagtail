# Wagtail API

This project exposes a custom Wagtail API from:

- `/api/v2/`

The API is built on Wagtail's v2 API router with custom endpoint viewsets in `app/api/urls`.

## Authentication

API authentication is controlled by `WAGTAILAPI_AUTHENTICATION`.

When enabled, endpoints require authentication via one of:

- API token (recommended for services)
- Authenticated Wagtail admin session user

Token and session fallback is implemented by `TokenOrUserAuthentication` in `app/api/auth.py`.

For API token management commands, see [API tokens](../infrastructure/api-tokens.md).

## Endpoint overview

All API endpoints are registered in `app/api/urls/__init__.py`.

## How to add a new endpoint

Use this workflow when creating new API routes.

### 1. Choose the endpoint type

Pick the base class based on response shape:

- Extend `CustomPagesAPIViewSet` when returning Wagtail page content with page filters, pagination, and default page serialization behavior.
- Extend `GenericViewSet` when returning non-page or aggregate payloads.
- Extend a specific Wagtail endpoint class (for example `ImagesAPIViewSet` or `MediaAPIViewSet`) when you need to customize existing Wagtail endpoints.

### 2. Create a new viewset module

Create a file in `app/api/urls/`, for example `app/api/urls/my_feature.py`.

Page-based example:

```python
from wagtail.api.v2.views import path

from app.api.urls.pages import CustomPagesAPIViewSet
from app.my_feature.models import MyFeaturePage


class MyFeatureAPIViewSet(CustomPagesAPIViewSet):
    model = MyFeaturePage
    known_query_parameters = CustomPagesAPIViewSet.known_query_parameters.union(
        ["my_filter"]
    )

    @classmethod
    def get_urlpatterns(cls):
        return [
            path("", cls.as_view({"get": "listing_view"}), name="listing"),
        ]
```

Aggregate/custom-response example:

```python
from django.conf import settings
from django.urls import path
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.api.permissions import IsAPITokenAuthenticated


class MySummaryAPIViewSet(GenericViewSet):
    if settings.WAGTAILAPI_AUTHENTICATION:
        permission_classes = (IsAPITokenAuthenticated,)

    def summary_view(self, request):
        return Response({"status": "ok"})

    @classmethod
    def get_urlpatterns(cls):
        return [
            path("summary/", cls.as_view({"get": "summary_view"}), name="summary"),
        ]
```

### 3. Register the endpoint in the API router

Edit `app/api/urls/__init__.py`:

```python
from app.api.urls.my_feature import MyFeatureAPIViewSet

api_router.register_endpoint("my_feature", MyFeatureAPIViewSet)
```

This mounts the endpoint at `/api/v2/my_feature/`.

### 4. Add filters or query parameters (if needed)

- Put reusable filters in `app/api/filters.py`.
- Add accepted params to `known_query_parameters` to avoid "unknown parameter" errors.
- Keep validation errors explicit by raising `BadRequestError` with a clear message.

### 5. Apply auth rules consistently

If the endpoint should follow normal API auth behavior, add:

```python
if settings.WAGTAILAPI_AUTHENTICATION:
    permission_classes = (IsAPITokenAuthenticated,)
```

Only skip this when an endpoint is intentionally public.

### 6. Add tests

Create or update tests in `app/api/tests/`:

- success response shape
- auth required vs disabled behavior
- filter/query param validation
- edge cases (empty results, invalid inputs)

Run:

```sh
docker compose exec app poetry run pytest app/api/tests
```

## Project extensions to the default Wagtail API

### 1. Extended page responses

`CustomPagesAPIViewSet` extends `PagesAPIViewSet` with:

- `meta.breadcrumbs` in page detail responses
- additional `meta` fields: `privacy`, `last_published_at`, `url`, `depth`
- support for `html_path` lookup, including redirect resolution
- support for `descendant_of_path` filtering
- support for `author` filtering and alias handling (`include_aliases`)

### 2. Privacy-aware page detail behavior

For restricted pages:

- list responses exclude restricted subtrees
- detail responses return a locked payload with privacy metadata
- password-protected pages can be fetched by passing `password` in query params

### 3. Site-aware querying

Several endpoints use site-aware filtering:

- `site` query parameter support for site-specific content
- fallback to the default Wagtail site where appropriate
- redirects endpoint includes both site-specific and global redirects

### 4. Custom serializers and payloads

- `DefaultPageSerializer` builds response data from each page model's `default_api_fields` and `api_fields`.
- Images and media endpoints use UUID-based lookup and include custom payload fields.
- Global and catalogue endpoints provide aggregate, frontend-oriented payloads.

## Endpoint-specific behavior

### Pages: `/api/v2/pages/`

Custom query parameters include:

- `password`
- `author`
- `include_aliases`
- `descendant_of_path`
- standard Wagtail API query parameters

Useful patterns:

- Resolve by route path: `?html_path=/some/path/`
- Filter to a tree branch: `?descendant_of_path=/education/`
- Include aliases: `?include_aliases=true`

### Blog posts: `/api/v2/blog_posts/`

Adds filters:

- `year`
- `month` (requires `year`)
- `day` (requires `year` and `month`)
- `author`

Adds custom endpoints:

- `/api/v2/blog_posts/count/` for grouped post totals by year/month
- `/api/v2/blog_posts/authors/` for author/post counts

### Education resources and sessions

- `/api/v2/education/resources/` supports taxonomy filters:
  - `key_stage`
  - `time_period`
  - `theme`
- `/api/v2/education/sessions/` supports taxonomy and location filters:
  - `key_stage`, `time_period`, `theme`
  - `location`, `region`

Session listings also apply a current-or-future filter.

### Events: `/api/v2/events/`

Supports:

- location filters: `online`, `at_tna`
- inclusive date range filters: `from`, `to` (ISO date)

### Redirects: `/api/v2/redirects/`

Extensions include:

- `is_permanent` in payloads
- `site` filter support

### Page preview: `/api/v2/page_preview/`

Preview lookups require:

- `content_type` in `app_label.model` format
- preview `token`

This endpoint resolves content via `wagtail_headless_preview`.

### Article tags: `/api/v2/article_tags/`

Supports:

- `tags` as comma-separated slugs (required)
- optional `limit` (defaults to `3`)

### Images and media

- `/api/v2/images/` uses UUIDs and includes generated rendition metadata.
- `/api/v2/media/` uses UUIDs and includes chapters/subtitles metadata.

### Globals and catalogue

- `/api/v2/globals/notifications/` returns global alert and mourning notice data.
- `/api/v2/globals/navigation/` returns primary/secondary/footer navigation blocks.
- `/api/v2/catalogue/landing/` returns homepage notification data plus "explore the collection" sections.

## Related docs

- [API tokens](../infrastructure/api-tokens.md)
- [Environment variables](../env-vars.md)
- [Backend development](../development/backend.md)
