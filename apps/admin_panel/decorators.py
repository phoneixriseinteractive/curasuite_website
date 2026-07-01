"""CuraSuite — Admin Panel Access Decorators"""
from functools import wraps
from django.shortcuts import redirect


def admin_required(view_func):
    """Require authenticated staff user. Redirects to admin login otherwise."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/manage/login/?next={request.path}")
        if not request.user.is_staff:
            return redirect("/manage/login/?error=access_denied")
        return view_func(request, *args, **kwargs)
    return wrapper
