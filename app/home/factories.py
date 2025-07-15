from app.core.factories import BasePageFactory
from app.home import models as app_models


class HomePageFactory(BasePageFactory):
    class Meta:
        model = app_models.HomePage
