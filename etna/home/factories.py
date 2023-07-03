from etna.core.factories import BasePageFactory
from etna.home import models as app_models


class HomePageFactory(BasePageFactory):
    class Meta:
        model = app_models.HomePage
