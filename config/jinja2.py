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


def url_for(view_name, *args, **kwargs):
    return reverse(view_name, args=args or None, kwargs=kwargs or None)


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
                "WAGTAILADMIN_BASE_URL": settings.WAGTAILADMIN_BASE_URL,
            },
            "url_for": url_for,
            "now_iso_8601": now_iso_8601,
        }
    )
    return env
