from app.cookies import models as app_models
from app.core.factories import BasePageFactory


class CookiesPageFactory(BasePageFactory):
    class Meta:
        model = app_models.CookiesPage
