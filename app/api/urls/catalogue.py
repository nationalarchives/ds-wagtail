from django.urls import path
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.alerts.models import AlertSerializer
from app.articles.models import ArticleIndexPage
from app.collections.models import ExplorerIndexPage
from app.core.models import BasePage
from app.core.serializers import MourningSerializer
from app.core.serializers.pages import DefaultPageSerializer
from app.home.models import HomePage


class CatalogueAPIViewSet(GenericViewSet):

    model = BasePage

    def landing_view(self, request):
        homepage_global_notification = HomePage.objects.first().global_alert
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
        explore_the_collection_top_pages = (
            ExplorerIndexPage.objects.first().get_children().all().live()
        )
        explore_the_collection_latest_articles = (
            ArticleIndexPage.objects.first()
            .get_children()
            .all()
            .live()
            .order_by("-first_published_at")[:3]
        )
        return Response(
            {
                "global_alert": global_alert,
                "mourning_notice": mourning_notice,
                "explore_the_collection": {
                    "top_pages": DefaultPageSerializer(
                        explore_the_collection_top_pages, many=True
                    ).data,
                    "latest_articles": DefaultPageSerializer(
                        explore_the_collection_latest_articles, many=True
                    ).data,
                },
            }
        )

    @classmethod
    def get_urlpatterns(cls):
        """
        This returns a list of URL patterns for the endpoint
        """
        return [
            path("landing/", cls.as_view({"get": "landing_view"}), name="landing"),
        ]
