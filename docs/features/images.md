# Images

## Overview

The image system is built on top of Wagtail's image infrastructure and extends it with:

- A custom image model (`CustomImage`) that stores additional metadata such as transcriptions, translations, and copyright information.
- A custom serializer (`ImageSerializer` / `DetailedImageSerializer`) that generates multiple format renditions (JPEG, WebP, and optionally others) in a single API field.
- A standalone `image_generator` function that can be called directly when the serializer isn't convenient.
- A custom `APIImageChooserBlock` for use in StreamField blocks.
- A dedicated `/images` API endpoint that exposes the image library.

---

## The `CustomImage` model

`app/images/models.py`

Extends Wagtail's `AbstractImage` with the following extra fields:

| Field                   | Type            | Notes                                                                                |
| ----------------------- | --------------- | ------------------------------------------------------------------------------------ |
| `uuid`                  | `UUIDField`     | Auto-generated, unique, read-only. Used as the lookup key in the `/images` endpoint. |
| `title`                 | `CharField`     | Descriptive name. Shown in highlights galleries.                                     |
| `description`           | `CharField`     | Alt text for the image.                                                              |
| `copyright`             | `RichTextField` | Credit for images not owned by TNA. Do not include the copyright symbol.             |
| `transcription_heading` | `CharField`     | Choice of `"Transcript"` or `"Partial transcript"`.                                  |
| `transcription`         | `RichTextField` | Optional text transcription of the image content.                                    |
| `translation_heading`   | `CharField`     | Choice of `"Translation"` or `"Modern English"`.                                     |
| `translation`           | `RichTextField` | Optional English translation of the transcription.                                   |

The companion model `CustomImageRendition` extends `AbstractRendition` and adds a `full_url` property.

---

## Serializers

`app/core/serializers/images.py`

### `ImageSerializer`

The primary serializer for images in API responses. It generates JPEG and WebP renditions in a single field, rather than requiring separate API calls or multiple `ImageRenditionField`s.

**Parameters**

| Parameter                    | Default            | Description                                                                                |
| ---------------------------- | ------------------ | ------------------------------------------------------------------------------------------ |
| `rendition_size`             | `"fill-600x400"`   | Wagtail rendition size string applied to the primary rendition.                            |
| `jpeg_quality`               | `60`               | JPEG compression quality (1–100) for the primary rendition.                                |
| `webp_quality`               | `70`               | WebP compression quality (1–100) for the primary rendition.                                |
| `background_colour`          | `"fff"`            | Hex colour (without `#`) used to fill transparent areas.                                   |
| `formats`                    | `["jpeg", "webp"]` | List of output formats. Any Wagtail-supported format string can be added (e.g. `"png"`).   |
| `additional_rendition_specs` | `None`             | Dict of named extra renditions. See [Additional renditions](#additional-renditions) below. |

**Usage**

```python
from wagtail.api import APIField
from app.core.serializers import ImageSerializer

api_fields = [
    APIField("image", serializer=ImageSerializer()),
]
```

**API response shape**

```json
"image": {
  "id": 1,
  "uuid": "a1b2c3d4-...",
  "title": "Example image",
  "description": "Alt text for the image",
  "jpeg": {
    "url": "/media/images/example.jpg",
    "full_url": "https://example.com/media/images/example.jpg",
    "width": 600,
    "height": 400
  },
  "webp": {
    "url": "/media/images/example.webp",
    "full_url": "https://example.com/media/images/example.webp",
    "width": 600,
    "height": 400
  }
}
```

### `DetailedImageSerializer`

Extends `ImageSerializer` with additional metadata fields intended for in-page image use (e.g. hero images, article body images), rather than teaser/thumbnail use.

Extra fields added to the response:

| Key           | Value                                                         |
| ------------- | ------------------------------------------------------------- |
| `transcript`  | `{"heading": "Transcript", "text": "<rich text>"}` or `null`  |
| `translation` | `{"heading": "Translation", "text": "<rich text>"}` or `null` |
| `copyright`   | Copyright string or `null`                                    |

```python
from app.core.serializers import DetailedImageSerializer

APIField("hero_image", serializer=DetailedImageSerializer(rendition_size="fill-1800x720"))
```

---

## Additional renditions

Both `ImageSerializer` and `APIImageChooserBlock` accept an `additional_rendition_specs` parameter that generates extra named renditions alongside the primary one.

Each key in the dict becomes the prefix of the output key in the API response (suffixed with the format name).

### Simple form - size string only

Uses the top-level `jpeg_quality` and `webp_quality` values.

```python
ImageSerializer(
    rendition_size="fill-1800x720",
    additional_rendition_specs={
        "small": "fill-900x360",
    },
)
```

Response keys produced: `jpeg`, `webp`, `small_jpeg`, `small_webp`.

### Extended form - size with per-rendition quality overrides

Pass a dict with a `size` key and optional `jpeg_quality` / `webp_quality` keys to override quality for that specific rendition only. Any quality not specified falls back to the top-level value.

```python
ImageSerializer(
    rendition_size="fill-600x400",
    jpeg_quality=60,
    webp_quality=70,
    additional_rendition_specs={
        "small": "fill-300x200",  # uses default qualities
        "large": {
            "size": "fill-1200x800",
            "jpeg_quality": 85,
            "webp_quality": 90,
        },
    },
)
```

Response keys produced: `jpeg`, `webp`, `small_jpeg`, `small_webp`, `large_jpeg`, `large_webp`.

The two forms can be mixed freely in the same dict.

---

## `image_generator` function

`app/core/serializers/images.py`

A standalone function that can be called directly when you need rendition data outside the serializer context (e.g. in the `/images` API view).

```python
from app.core.serializers.images import image_generator

image_data = image_generator(
    original_image=my_image,
    rendition_size="max-900x900",
    jpeg_quality=60,
    webp_quality=70,
    background_colour="fff",
    formats=["jpeg", "webp"],
    additional_rendition_specs={
        "thumb": {"size": "fill-128x128", "jpeg_quality": 50},
    },
)
```

Returns a dict of rendition dicts keyed by format/spec name, or `None` if the image is falsy or no renditions were produced. All renditions are fetched in a single `get_renditions()` call for efficiency.

### `image_generator` additional formats

When required, the `image_generator` function (and users of this function) can be passed a `formats` parameter (`list[]`). For example, `["jpeg", "webp", "png"]` - this will generate `jpeg`, `webp`, and `png` formats of an image in the same representation.

---

## `APIImageChooserBlock`

`app/core/blocks/image.py`

A Wagtail `ImageChooserBlock` subclass for use in StreamField block definitions. Instead of returning a raw image ID, `get_api_representation` returns the same structured dict as `DetailedImageSerializer`.

**Parameters**

| Parameter                    | Default          | Description                                                |
| ---------------------------- | ---------------- | ---------------------------------------------------------- |
| `rendition_size`             | `"fill-600x400"` | Wagtail rendition size string.                             |
| `jpeg_quality`               | `60`             | JPEG quality for the primary rendition.                    |
| `webp_quality`               | `70`             | WebP quality for the primary rendition.                    |
| `background_colour`          | `"fff"`          | Background fill colour (hex, no `#`).                      |
| `additional_rendition_specs` | `None`           | Named extra renditions - same format as `ImageSerializer`. |

```python
from app.core.blocks.image import APIImageChooserBlock

image = APIImageChooserBlock(
    rendition_size="fill-1800x720",
    additional_rendition_specs={"small": "fill-900x360"},
)
```

---

## `/images` API endpoint

`app/api/urls/images.py`

Exposes the image library at `/api/v2/images/`. Images are looked up by `uuid` rather than the Wagtail default integer `id`.

The endpoint uses `ViewSetImageSerializer`, which inherits from Wagtail's built-in `ImageSerializer` and injects rendition data via `image_generator`. Default rendition settings:

| Setting             | Value           |
| ------------------- | --------------- |
| `rendition_size`    | `"max-900x900"` |
| `jpeg_quality`      | `60`            |
| `webp_quality`      | `70`            |
| `background_colour` | `"fff"`         |

Access can be restricted to authenticated API token holders via the `WAGTAILAPI_AUTHENTICATION` setting.

Extra fields exposed in the response: `uuid`, `title`, `copyright`, `tags`, `transcription_heading`, `transcription`, `translation_heading`, `translation`, `description`, plus the standard `jpeg` / `webp` rendition objects.
