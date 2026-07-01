"""CuraSuite — Newsletter Views"""
from django.http import Http404
from django.shortcuts import render, redirect
from .forms import NewsletterSubscribeForm
from .services import confirm_subscription, subscribe, unsubscribe_by_token


def subscribe_view(request):
    if request.method != "POST":
        return redirect("/")

    form = NewsletterSubscribeForm(request.POST)
    if form.is_valid():
        d = form.cleaned_data
        subscribe(
            email=d["email"],
            first_name=d.get("first_name", ""),
            source="website_footer",
            ip_address=request.META.get("REMOTE_ADDR"),
            referrer=request.META.get("HTTP_REFERER", ""),
        )
        if request.headers.get("HX-Request"):
            return render(request, "newsletter/partials/subscribe_success.html")
        return redirect("newsletter:subscribe_success")

    if request.headers.get("HX-Request"):
        return render(request, "newsletter/partials/subscribe_form.html", {"form": form})
    return redirect("/")


def subscribe_success(request):
    return render(request, "newsletter/subscribe_success.html")


def confirm(request, token):
    subscriber = confirm_subscription(str(token))
    if not subscriber:
        raise Http404("Invalid or expired confirmation link.")
    return render(request, "newsletter/confirmed.html", {"subscriber": subscriber})


def unsubscribe_view(request, token):
    if request.method == "POST":
        reason = request.POST.get("reason", "")
        subscriber = unsubscribe_by_token(str(token), reason=reason)
        if not subscriber:
            raise Http404("Invalid unsubscribe link.")
        return render(request, "newsletter/unsubscribed.html", {"subscriber": subscriber})

    subscriber = NewsletterSubscriber = None
    from .selectors import get_subscriber_by_unsubscribe_token
    subscriber = get_subscriber_by_unsubscribe_token(token)
    if not subscriber:
        raise Http404("Invalid unsubscribe link.")
    return render(request, "newsletter/unsubscribe_confirm.html", {"subscriber": subscriber, "token": token})


def track_open(request, token):
    """1×1 pixel open tracking endpoint."""
    from django.http import HttpResponse
    from .models import NewsletterSend
    try:
        send = NewsletterSend.objects.get(tracking_token=token)
        send.mark_opened()
    except NewsletterSend.DoesNotExist:
        pass
    # Return transparent 1×1 GIF
    pixel = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
    return HttpResponse(pixel, content_type="image/gif")
