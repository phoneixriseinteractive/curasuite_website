"""CuraSuite — Admin Panel Services (2FA session/cookie glue for /manage/ login)"""
import secrets

from django.conf import settings
from django.core import signing

from apps.accounts.models import User
from apps.accounts.services import create_remembered_device, get_remembered_device

PENDING_2FA_SALT = "admin_panel.pending_2fa"
REMEMBER_DEVICE_SALT = "admin_panel.remember_device"

PENDING_2FA_SESSION_KEY = "admin_pending_2fa"
PENDING_2FA_REMEMBER_ME_KEY = "admin_pending_2fa_remember_me"


def client_ip(request) -> str:
    return request.META.get("REMOTE_ADDR")


def set_pending_2fa(request, user, remember_me: bool) -> None:
    request.session[PENDING_2FA_SESSION_KEY] = signing.dumps({"uid": str(user.pk)}, salt=PENDING_2FA_SALT)
    request.session[PENDING_2FA_REMEMBER_ME_KEY] = bool(remember_me)


def get_pending_2fa_user(request):
    token = request.session.get(PENDING_2FA_SESSION_KEY)
    if not token:
        return None
    try:
        data = signing.loads(token, salt=PENDING_2FA_SALT, max_age=settings.ADMIN_OTP_TTL_MINUTES * 60)
    except signing.BadSignature:
        return None
    return User.objects.filter(pk=data["uid"], is_staff=True).first()


def clear_pending_2fa(request) -> None:
    request.session.pop(PENDING_2FA_SESSION_KEY, None)
    request.session.pop(PENDING_2FA_REMEMBER_ME_KEY, None)


def issue_remember_device_cookie(response, request, user) -> None:
    raw_token = secrets.token_urlsafe(32)
    create_remembered_device(
        user, raw_token,
        ip_address=client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    signed = signing.TimestampSigner(salt=REMEMBER_DEVICE_SALT).sign(raw_token)
    response.set_cookie(
        settings.ADMIN_REMEMBER_DEVICE_COOKIE_NAME,
        signed,
        max_age=settings.ADMIN_REMEMBER_DEVICE_DAYS * 86400,
        secure=not settings.DEBUG,
        httponly=True,
        samesite="Lax",
        path="/manage/",
    )


def check_remembered_device(request, user):
    raw_signed = request.COOKIES.get(settings.ADMIN_REMEMBER_DEVICE_COOKIE_NAME)
    if not raw_signed:
        return None
    try:
        raw_token = signing.TimestampSigner(salt=REMEMBER_DEVICE_SALT).unsign(
            raw_signed, max_age=settings.ADMIN_REMEMBER_DEVICE_DAYS * 86400
        )
    except signing.BadSignature:
        return None
    return get_remembered_device(user, raw_token)
