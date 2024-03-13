from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render



def client_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and not u.is_staff,
        login_url=None,
    )
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.is_staff:
            return render(request, "management/unauth.html")
        return function(request, *args, **kwargs)
    return wrapper if function else actual_decorator

def staff_only(function):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return render(request, "management/unauth.html")
        return function(request, *args, **kwargs)
    return wrapper


