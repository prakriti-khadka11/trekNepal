# decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def guide_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect("login")
        if not hasattr(user, "guide"):
            messages.error(request, "You must be logged in as a guide to access this page.")
            return redirect("login")
        if not user.guide.verified:
            messages.error(request, "Your guide account is pending admin approval.")
            return redirect("guide_login")
        return view_func(request, *args, **kwargs)
    return wrapper


def user_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect("login")
        if hasattr(user, "guide"):
            messages.error(request, "Guides cannot access this page.")
            return redirect("guide_dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper
