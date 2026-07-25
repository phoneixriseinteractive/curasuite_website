"""CuraSuite — Accounts Services (login OTP + remembered devices)"""
import hashlib
import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import LoginOTP, RememberedDevice

logger = logging.getLogger(__name__)


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def generate_otp_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def send_otp_email(user, code: str) -> None:
    send_mail(
        subject="Your CuraSuite Admin verification code",
        message=(
            f"Hi {user.short_name},\n\n"
            f"Your one-time verification code is: {code}\n\n"
            f"This code expires in {settings.ADMIN_OTP_TTL_MINUTES} minutes. "
            f"If you did not attempt to sign in, you can ignore this email.\n\n"
            f"— The CuraSuite Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def create_and_send_otp(user, ip_address: str = None, user_agent: str = "") -> LoginOTP:
    """Invalidate any prior unused codes, create a new one, and email it. Raises on send failure."""
    LoginOTP.objects.filter(user=user, is_used=False).update(is_used=True, consumed_at=timezone.now())
    code = generate_otp_code()
    otp = LoginOTP.objects.create(
        user=user,
        code_hash=_hash(code),
        expires_at=timezone.now() + timedelta(minutes=settings.ADMIN_OTP_TTL_MINUTES),
        ip_address=ip_address,
        user_agent=user_agent[:255],
    )
    send_otp_email(user, code)
    return otp


def resend_otp(user, ip_address: str = None, user_agent: str = "") -> tuple[bool, str | None]:
    window_start = timezone.now() - timedelta(minutes=settings.ADMIN_OTP_SEND_WINDOW_MINUTES)
    if LoginOTP.objects.filter(user=user, created_at__gte=window_start).count() >= settings.ADMIN_OTP_MAX_SENDS_PER_WINDOW:
        return False, "too_many_requests"

    last = LoginOTP.objects.filter(user=user).order_by("-created_at").first()
    if last and (timezone.now() - last.created_at).total_seconds() < settings.ADMIN_OTP_RESEND_COOLDOWN_SECONDS:
        return False, "cooldown"

    try:
        create_and_send_otp(user, ip_address, user_agent)
    except Exception:
        logger.exception("Failed to resend admin OTP email to %s", user.email)
        return False, "send_failed"
    return True, None


def verify_otp(user, raw_code: str) -> tuple[bool, str | None]:
    otp = (
        LoginOTP.objects.filter(user=user, is_used=False, expires_at__gt=timezone.now())
        .order_by("-created_at")
        .first()
    )
    if otp is None:
        return False, "Your code has expired. Please request a new one."
    if otp.attempts >= settings.ADMIN_OTP_MAX_ATTEMPTS:
        return False, "Too many incorrect attempts. Please request a new code."

    if _hash(raw_code.strip()) != otp.code_hash:
        otp.attempts += 1
        otp.save(update_fields=["attempts", "updated_at"])
        return False, "Incorrect code. Please try again."

    otp.is_used = True
    otp.consumed_at = timezone.now()
    otp.save(update_fields=["is_used", "consumed_at", "updated_at"])
    return True, None


def create_remembered_device(user, raw_token: str, ip_address: str = None, user_agent: str = "") -> RememberedDevice:
    return RememberedDevice.objects.create(
        user=user,
        token_hash=_hash(raw_token),
        expires_at=timezone.now() + timedelta(days=settings.ADMIN_REMEMBER_DEVICE_DAYS),
        ip_address=ip_address,
        user_agent=user_agent[:255],
    )


def get_remembered_device(user, raw_token: str) -> RememberedDevice | None:
    device = RememberedDevice.objects.filter(
        token_hash=_hash(raw_token),
        user=user,
        revoked_at__isnull=True,
        expires_at__gt=timezone.now(),
    ).first()
    if device:
        device.last_used_at = timezone.now()
        device.save(update_fields=["last_used_at"])
    return device
