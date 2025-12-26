from django.urls import path
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.alerts.models import AlertSerializer
from app.api.utils import get_site_from_request
from app.core.models import BasePage
from app.core.serializers import MourningSerializer
from app.home.models import HomePage


class GlobalsAPIViewSet(GenericViewSet):

    model = BasePage

    def notifications_view(self, request):
        site = get_site_from_request(request)

        # If no site found, return empty notifications
        if not site:
            return Response(
                {
                    "global_alert": None,
                    "mourning_notice": None,
                }
            )

        # Get the HomePage for specific site
        try:
            homepage = HomePage.objects.get(id=site.root_page_id)
        except HomePage.DoesNotExist:
            # If the root page isn't a HomePage, set notifications to None
            return Response(
                {
                    "global_alert": None,
                    "mourning_notice": None,
                }
            )

        homepage_global_notification = homepage.global_alert
        global_alert = (
            AlertSerializer(homepage_global_notification).data
            if homepage_global_notification and homepage_global_notification.cascade
            else None
        )
        homepage_mourning_notice = HomePage.objects.first().mourning_notice
        mourning_notice = (
            MourningSerializer(homepage_mourning_notice).data
            if homepage_mourning_notice
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
