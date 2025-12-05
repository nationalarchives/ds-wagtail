import os
from urllib.parse import urlparse

from django.views.generic import TemplateView
from wagtail.admin.userbar import Userbar


class UserbarView(TemplateView):
    template_name = Userbar.template_name
    http_method_names = ["get"]

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        headless_preview_url = urlparse(
            os.getenv(
                "WAGTAIL_HEADLESS_PREVIEW_URL",
                "https://www.nationalarchives.gov.uk/preview/",
            )
        )
        origin = f"{headless_preview_url.scheme}://{headless_preview_url.netloc}"
        response["Access-Control-Allow-Origin"] = origin
        return response

    def get_context_data(self, **kwargs):
        return Userbar(object=None, position="bottom-right").get_context_data(
            super().get_context_data(request=self.request, **kwargs)
        )
