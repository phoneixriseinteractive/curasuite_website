"""
CuraSuite — SEO Redirect Middleware
Processes active redirects before the URL resolver runs.
"""

from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect

from .selectors import get_redirect_for_path


class RedirectMiddleware:
    """
    Check the Redirect table for any matching path and redirect accordingly.
    Sits early in the middleware stack so it fires before view routing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        redirect = get_redirect_for_path(request.path_info)
        if redirect:
            if redirect.redirect_type == "301":
                return HttpResponsePermanentRedirect(redirect.new_path)
            return HttpResponseRedirect(redirect.new_path)
        return self.get_response(request)
