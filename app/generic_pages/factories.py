from app.core.factories import BasePageFactory
from app.generic_pages import models as app_models


class GeneralPageFactory(BasePageFactory):
    class Meta:
        model = app_models.GeneralPage
