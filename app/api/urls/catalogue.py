from app.alerts.models import AlertSerializer
from app.api.permissions import IsAPITokenAuthenticated
from app.articles.models import ArticleIndexPage
from app.collections.models import ExplorerIndexPage
from app.core.models import BasePage
from app.core.serializers import MourningSerializer
from app.core.serializers.pages import DefaultPageSerializer
from app.home.models import HomePage
from django.conf import settings
from django.urls import path
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from wagtail.models import Site


class CatalogueAPIViewSet(GenericViewSet):
    if settings.WAGTAILAPI_AUTHENTICATION:
        permission_classes = (IsAPITokenAuthenticated,)

    model = BasePage

    def landing_view(self, request):
        site = Site.objects.get(is_default_site=True)
        homepage = HomePage.objects.get(id=site.root_page_id)

        homepage_global_notification = homepage.global_alert
        global_alert = (
            AlertSerializer(homepage_global_notification).data
            if homepage_global_notification and homepage_global_notification.cascade
            else None
        )
        homepage_mourning_notice = homepage.mourning_notice
        mourning_notice = (
            MourningSerializer(homepage_mourning_notice).data
            if homepage_mourning_notice
            else None
        )

        explorer_index = (
            ExplorerIndexPage.objects.live().descendant_of(site.root_page).first()
        )
        explore_the_collection_top_pages = (
            explorer_index.get_children().all().live() if explorer_index else []
        )

        article_index = (
            ArticleIndexPage.objects.live().descendant_of(site.root_page).first()
        )
        explore_the_collection_latest_articles = (
            article_index.get_children()
            .all()
            .live()
            .order_by("-first_published_at")[:3]
            if article_index
            else []
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
