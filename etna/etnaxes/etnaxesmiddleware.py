from typing import Callable

from allauth.account.forms import LoginForm
from axes.helpers import get_failure_limit, get_client_username
from django.conf import settings
from django.shortcuts import render

from axes.middleware import AxesMiddleware


class AxesEtnaMiddleware(AxesMiddleware):
    def __init__(self, get_response: Callable):
        super(AxesEtnaMiddleware, self).__init__(get_response)

    def __call__(self, request):
        response = self.get_response(request)
        return response
