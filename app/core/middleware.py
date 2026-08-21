import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django_otp.plugins.otp_static.models import StaticDevice

# Don't include commonly misunderstood characters
ALLOWED_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
RECOVERY_CODES_CACHE_NAMESPACE = "core:wagtail:recovery_codes"
RECOVERY_CODES_CACHE_TIMEOUT = getattr(settings, "RECOVERY_CODES_CACHE_TIMEOUT", 300)


def get_recovery_codes_cache_key(user, nonce=None):
    if nonce:
        return f"{RECOVERY_CODES_CACHE_NAMESPACE}:u{user.pk}:n{nonce}"
    return f"{RECOVERY_CODES_CACHE_NAMESPACE}:u{user.pk}"


def create_static_device_with_tokens(
    user,
    count=10,
    length=16,
    allowed_chars=ALLOWED_CHARS,
    device_name="Recovery codes",
    delete_existing=False,
):
    logger = logging.getLogger(__name__)

    with transaction.atomic():
        # Serialize generation per user to prevent duplicate devices/tokens
        get_user_model().objects.select_for_update().only("pk").get(pk=user.pk)

        existing_qs = StaticDevice.objects.filter(user=user)
        existing_count = existing_qs.count()

        if existing_count > 1:
            logger.warning(
                "Multiple StaticDevice objects found for user %s (count=%d). Removing duplicates.",
                getattr(user, "pk", "<unknown>"),
                existing_count,
            )
            existing_qs.delete()
            logger.info(
                "Removed %d duplicate StaticDevice(s) for user %s",
                existing_count,
                getattr(user, "pk", "<unknown>"),
            )
        elif existing_count == 1 and not delete_existing:
            device = existing_qs.first()
            codes = list(device.token_set.values_list("token", flat=True))
            return device, codes

        # Create a fresh StaticDevice and tokens
        StaticDevice.objects.filter(user=user).delete()
        device = StaticDevice.objects.create(
            user=user, name=device_name, confirmed=True
        )

        codes = [
            get_random_string(length=length, allowed_chars=allowed_chars)
            for _ in range(count)
        ]
        for code in codes:
            device.token_set.create(token=code)

        logger.info(
            "Generated %d recovery codes for user %s",
            len(codes),
            getattr(user, "pk", "<unknown>"),
        )

        return device, codes


class RecoveryCodesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._should_generate_recovery_codes(request):
            return self._bootstrap_and_redirect(request)

        return self.get_response(request)

    def _should_generate_recovery_codes(self, request):
        # Only generate recovery codes for verified, authenticated GET requests not on a 2FA/recovery/logout page
        if not (
            getattr(settings, "WAGTAIL_2FA_REQUIRED", False) and request.method == "GET"
        ):
            return False

        user = getattr(request, "user", None)
        if not (
            user
            and user.is_authenticated
            and callable(getattr(user, "is_verified", None))
            and user.is_verified()
        ):
            return False

        recovery_path = reverse("recovery_codes")
        logout_path = reverse("wagtailadmin_logout")
        path = request.path

        if path == recovery_path or "/2fa/" in path or path == logout_path:
            return False

        return not StaticDevice.objects.filter(user=user).exists()

    def _bootstrap_and_redirect(self, request):
        _, codes = create_static_device_with_tokens(request.user, delete_existing=False)

        # One-time nonce stored in session to prevent direct GET access to the recovery page.
        nonce = get_random_string(length=12)
        request.session["initial_recovery_codes"] = codes
        request.session["initial_recovery_nonce"] = nonce

        # Backup in cache keyed by nonce so parallel redirects that consumed the session
        # can still render the codes if they carry the session nonce.
        cache.set(
            get_recovery_codes_cache_key(request.user, nonce),
            codes,
            timeout=RECOVERY_CODES_CACHE_TIMEOUT,
        )
        return redirect("recovery_codes")
