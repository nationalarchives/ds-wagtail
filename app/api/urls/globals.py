from django.urls import path
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from wagtail.models import Site

from app.alerts.models import AlertSerializer
from app.core.models import BasePage
from app.core.serializers import MourningSerializer
from app.home.models import HomePage


class GlobalsAPIViewSet(GenericViewSet):

    model = BasePage

    def notifications_view(self, request):
        """
        Returns global notifications for the default site.
        """
        site = Site.objects.get(is_default_site=True)
        homepage = HomePage.objects.get(id=site.root_page_id)

        global_alert = (
            AlertSerializer(homepage.global_alert).data
            if homepage.global_alert and homepage.global_alert.cascade
            else None
        )

        mourning_notice = (
            MourningSerializer(homepage.mourning_notice).data
            if homepage.mourning_notice
            else None
        )

        return Response(
            {
                "global_alert": global_alert,
                "mourning_notice": mourning_notice,
            }
        )

    @classmethod
    def get_urlpatterns(cls):
        """
        This returns a list of URL patterns for the endpoint
        """
        return [
            path(
                "notifications/",
                cls.as_view({"get": "notifications_view"}),
                name="notifications",
            ),
        ]
