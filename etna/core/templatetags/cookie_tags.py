import json

from json.decoder import JSONDecodeError
from typing import Union
from urllib.parse import unquote

from django import template

register = template.Library()


@register.filter
def cookie_use_permitted(value: Union[str, None]) -> bool:
    """
    Return the True/False based on cookie usage value
    if no cookie set it will return False
    """
    usage = False

    try:
        if value is not None:
            cookie_str = unquote(value)
            usage = json.loads(cookie_str)["usage"]
    except (
        JSONDecodeError,  # invalid json
        TypeError,  # decoded json isn't a dict
        KeyError,  # dict doesn't contain 'usage'
        ValueError,  # 'usage' value cannot be converted to boolean
    ):
        usage = False

    return usage
