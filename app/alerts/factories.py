from app.alerts import models as app_models
from wagtail_factories import PageFactory


class TestAlertPageFactory(PageFactory):
    """Factory for creating test pages with AlertMixin"""

    class Meta:
        model = app_models.TestAlertPage


class TestThemedAlertPageFactory(PageFactory):
    """Factory for creating test pages with ThemedAlertMixin"""

    class Meta:
        model = app_models.TestThemedAlertPage
