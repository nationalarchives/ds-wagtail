from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.template.response import TemplateResponse

User = get_user_model()


def beta_testers_report(request):
    """Basic report to list all beta tester to link user with activity in GA."""

    group = Group.objects.get(name="Beta Testers")
    users = group.user_set.all().order_by("id")

    return TemplateResponse(
        request,
        "users/index.html",
        {
            "users": users,
            "group": group,
        },
    )
