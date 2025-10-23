from app.core.factories import BasePageFactory
from app.foi import models as app_models


class FoiIndexPageFactory(BasePageFactory):
    class Meta:
        model = app_models.FoiIndexPage


class FoiRequestPageFactory(BasePageFactory):
    class Meta:
        model = app_models.FoiRequestPage
