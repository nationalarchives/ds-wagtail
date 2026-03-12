import json
import re
from datetime import datetime

from django import template
from django.conf import settings
from django.templatetags.static import StaticNode
from django.urls import reverse
from django.utils.safestring import mark_safe
from jinja2 import Environment

register = template.Library()


class StaticNodeWithVersion(StaticNode):
    @classmethod
    def handle_simple(cls, path, **kwargs):
        url = super().handle_simple(path)
        if kwargs:
            url += "?" + "&".join(
                [f"{parameter}={kwargs[parameter]}" for parameter in kwargs]
            )
        return mark_safe(url)


@register.tag("static")
def do_static_with_version(parser, token):
    return StaticNodeWithVersion.handle_token(parser, token)


def static_with_version(path, **kwargs):
    return StaticNodeWithVersion.handle_simple(path, **kwargs)


def slugify(s):
    if not s:
        return s
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s


def now_iso_8601():
    now = datetime.now()
    now_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return now_date


def environment(**options):
    env = Environment(**options)

    TNA_FRONTEND_VERSION = ""
    try:
        with open(
            "/app/node_modules/@nationalarchives/frontend/package.json",
        ) as package_json:
            try:
                data = json.load(package_json)
                TNA_FRONTEND_VERSION = data["version"] or ""
            except ValueError:
                pass
    except FileNotFoundError:
        pass

    env.globals.update(
        {
            "static": static_with_version,
            "app_config": {
                "ENVIRONMENT_NAME": settings.ENVIRONMENT_NAME,
                "GA4_ID": settings.GA4_ID,
                "CONTAINER_IMAGE": settings.CONTAINER_IMAGE,
                "BUILD_VERSION": settings.BUILD_VERSION,
                "TNA_FRONTEND_VERSION": TNA_FRONTEND_VERSION,
                "COOKIE_DOMAIN": settings.COOKIE_DOMAIN,
            },
            "url_for": reverse,
            "now_iso_8601": now_iso_8601,
        }
    )
    env.filters.update({"slugify": slugify})
    return env
