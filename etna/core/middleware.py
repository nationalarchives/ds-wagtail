from datetime import datetime, timedelta
from urllib.parse import quote

from django.conf import settings


class SetDefaultCookiePreferencesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not settings.FEATURE_COOKIE_BANNER_ENABLED:
            return response
        cookie_name = "cookies_policy"
        if not request.COOKIES.get(cookie_name, None):
            expires = datetime.utcnow() + timedelta(days=90)
            value = '{"usage":false,"settings":false,"essential":true}'
            response.set_cookie(
                cookie_name,
                expires=expires,
                path="/",
                domain=settings.COOKIE_DOMAIN,
                value=quote(value),
            )
        return response
