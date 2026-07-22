"""
CuraSuite — Integrations Services

CAPTCHA verification for lead-capture forms (contact, demo request, appointment
widget). The site key is public and lives in Site Settings; the secret key never
touches the browser, so it's read straight from the environment (matching how the
AI provider keys are handled — see apps/integrations/chatbot_views.py).
"""

import json
import logging
import os
import urllib.parse
import urllib.request

from .models import SiteSettings

logger = logging.getLogger(__name__)

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
RECAPTCHA_V3_MIN_SCORE = 0.5


def verify_captcha(request) -> bool:
    """
    Verify the CAPTCHA token attached to a POST request, per Site Settings.

    Fails OPEN (returns True, submission proceeds) when CAPTCHA is disabled, the
    secret key isn't configured in the environment, or the verification request
    itself errors out — a misconfigured key or a network hiccup with Google/
    Cloudflare should never silently block every lead on the site.

    Fails CLOSED (returns False, submission rejected) only on an explicit
    negative signal: no token submitted, or the provider says the token is
    invalid/expired, or (reCAPTCHA v3 only) the bot-likelihood score is too low.
    """
    settings_obj = SiteSettings.load()
    if not settings_obj.captcha_enabled or not settings_obj.captcha_site_key:
        return True

    is_turnstile = settings_obj.captcha_provider == "turnstile"
    secret = os.environ.get("TURNSTILE_SECRET_KEY" if is_turnstile else "RECAPTCHA_SECRET_KEY")
    if not secret:
        logger.warning(
            "CAPTCHA is enabled in Site Settings but no %s is set in the environment — "
            "allowing this submission through unverified.",
            "TURNSTILE_SECRET_KEY" if is_turnstile else "RECAPTCHA_SECRET_KEY",
        )
        return True

    token = request.POST.get("cf-turnstile-response" if is_turnstile else "g-recaptcha-response", "")
    if not token:
        return False

    data = urllib.parse.urlencode({
        "secret": secret,
        "response": token,
        "remoteip": request.META.get("REMOTE_ADDR", ""),
    }).encode()

    try:
        req = urllib.request.Request(
            TURNSTILE_VERIFY_URL if is_turnstile else RECAPTCHA_VERIFY_URL,
            data=data, method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read().decode())
    except Exception:
        logger.exception("CAPTCHA verification request failed — allowing submission through.")
        return True

    if not result.get("success"):
        logger.warning(
            "CAPTCHA verification rejected by %s: error-codes=%s hostname=%s",
            "Turnstile" if is_turnstile else "reCAPTCHA",
            result.get("error-codes"), result.get("hostname"),
        )
        return False
    if not is_turnstile and result.get("score", 1.0) < RECAPTCHA_V3_MIN_SCORE:
        logger.info("reCAPTCHA v3 score %.2f below threshold for this submission.", result.get("score", 0))
        return False
    return True
