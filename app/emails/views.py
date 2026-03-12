from django.shortcuts import render


def email(request):
    return render(request, "wagtailadmin/account/password_reset/email.txt")
