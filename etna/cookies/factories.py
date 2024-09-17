from etna.cookies import models as app_models
from etna.core.factories import BasePageFactory


class CookiesPageFactory(BasePageFactory):
    class Meta:
        model = app_models.CookiesPage
