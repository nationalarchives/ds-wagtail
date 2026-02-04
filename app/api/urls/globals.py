from app.alerts.models import AlertSerializer
from app.api.permissions import IsAPITokenAuthenticated
from app.api.utils import get_site_from_request
from app.core.models import BasePage
from app.core.serializers import MourningSerializer
from app.home.models import HomePage
from app.navigation.models import NavigationSettings
from django.conf import settings
from django.urls import path
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from wagtail.api.v2.serializers import StreamField as StreamFieldSerializer
from wagtail.models import Site


class GlobalsAPIViewSet(GenericViewSet):
    if settings.WAGTAILAPI_AUTHENTICATION:
        permission_classes = (IsAPITokenAuthenticated,)

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

    def navigation_view(self, request):
        """
        Navigation-specific endpoint for header and footer navigation.
        """
        site = get_site_from_request(request)

        if not site:
            return Response(
                {
                    "primary_navigation": [],
                    "secondary_navigation": [],
                    "footer_navigation": [],
                    "footer_links": [],
                }
            )

        navigation_settings = NavigationSettings.for_site(site)

        data = {
            "primary_navigation": (
                StreamFieldSerializer().to_representation(
                    navigation_settings.primary_navigation
                )
                if navigation_settings.primary_navigation
                else []
            ),
            "secondary_navigation": (
                StreamFieldSerializer().to_representation(
                    navigation_settings.secondary_navigation
                )
                if navigation_settings.secondary_navigation
                else []
            ),
            "footer_navigation": (
                StreamFieldSerializer().to_representation(
                    navigation_settings.footer_navigation
                )
                if navigation_settings.footer_navigation
                else []
            ),
            "footer_links": (
                StreamFieldSerializer().to_representation(
                    navigation_settings.footer_links
                )
                if navigation_settings.footer_links
                else []
            ),
        }

        return Response(data)

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
            path(
                "navigation/",
                cls.as_view({"get": "navigation_view"}),
                name="navigation",
            ),
        ]
