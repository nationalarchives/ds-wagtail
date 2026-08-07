import logging

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


def find_matching_users(predicate):
    qs = User.objects.filter(is_active=True)
    matches = []
    for u in qs:
        try:
            if predicate(u):
                matches.append(u)
        except Exception:
            continue

    return matches


def format_device_name(label, device):
    try:
        name = getattr(device, "name", "<unnamed>")
    except Exception:
        name = "<error>"

    return f"  - {label}: {name} (ID: {getattr(device, 'id', 'n/a')})"
