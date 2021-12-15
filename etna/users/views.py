from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group
from django.template.response import TemplateResponse

from etna.users.forms import AxesLoginForm

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


def login_view(request):
    if request.method == 'POST':
        try:
            user = authenticate(
                request=request,  # this is the important custom argument
                username=request.POST['login'],
                password=request.POST['password'],
            )
            form = AxesLoginForm(request.POST or None, request.FILES or None)
            if user is not None:
                form.login(request, user=user)
                if form.is_valid():
                    return redirect('/')
                else:
                    redirect(request.path)
            else:
                form.add_errors(request=request)
                return render(request, 'account/login.html', {'form': form})
        except BaseException as error:
            print('An exception occurred: {}'.format(error))
            if form is None:
                form = AxesLoginForm(request.POST or None, request.FILES or None)
            form.add_errors(request=request)
            return render(request, 'account/login.html', {'form': form})
    # Get request
    return render(request, 'account/login.html')
