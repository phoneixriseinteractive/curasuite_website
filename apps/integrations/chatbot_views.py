"""
CuraSuite — AI Chatbot Backend
Gemini-powered chatbot with 4-model fallback chain.
Pattern reused from CuraLabs: gemini-2.0-flash-lite → gemini-2.0-flash → gemini-1.5-flash-8b → gemini-2.5-flash
Distinguishes quota errors (skip immediately) from rate limits (short wait + retry).
"""

import json
import logging
import os
import time

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .models import SiteSettings

logger = logging.getLogger(__name__)

FALLBACK_MODELS = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash-8b",
    "gemini-2.5-flash",
]

_MAX_HISTORY = 10
_MAX_MESSAGE_LEN = 1000


def _get_system_prompt() -> str:
    try:
        s = SiteSettings.load()
        return s.chatbot_system_prompt or _default_system_prompt()
    except Exception:
        return _default_system_prompt()


def _default_system_prompt() -> str:
    return (
        "You are the CuraSuite Assistant, a helpful AI for CuraSuite — "
        "India's healthcare technology platform. Help visitors understand "
        "our products (CuraCMS, CuraLabs, CuraSuite), answer questions about "
        "features and pricing, and guide them to book a demo. "
        "Be friendly, professional, and concise. "
        "For medical advice, always direct users to qualified healthcare professionals."
    )


def _call_gemini(model: str, system_prompt: str, history: list, message: str) -> str:
    """Make a single Gemini API call. Raises on error."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise RuntimeError("google-genai package not installed. Run: pip install google-genai")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set.")

    client = genai.Client(api_key=api_key)

    contents = []
    for msg in history[-_MAX_HISTORY:]:
        role = "user" if msg.get("role") == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg.get("content", ""))]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=512,
            temperature=0.7,
        ),
    )
    return response.text


@csrf_protect
@require_POST
def chatbot_message(request):
    """
    POST /api/v1/chatbot/message/
    Body: { "message": "...", "history": [...] }
    Returns: { "reply": "...", "model": "..." }
    """
    # Check chatbot is enabled
    try:
        s = SiteSettings.load()
        if not s.chatbot_enabled:
            return JsonResponse({"error": "Chatbot is not enabled."}, status=403)
    except Exception:
        pass

    # Parse request
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    message = str(data.get("message", "")).strip()[:_MAX_MESSAGE_LEN]
    history = data.get("history", [])

    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)

    system_prompt = _get_system_prompt()

    # Try each model in the fallback chain
    last_error = None
    for model in FALLBACK_MODELS:
        try:
            reply = _call_gemini(model, system_prompt, history, message)
            logger.debug("Chatbot responded via %s", model)
            return JsonResponse({"reply": reply, "model": model})

        except Exception as e:
            error_str = str(e).upper()
            last_error = e

            # Quota exhausted — skip to next model immediately
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                if "DAILY" in error_str or "QUOTA" in error_str:
                    logger.warning("Quota exhausted for %s, trying next model", model)
                    continue
                # Per-minute rate limit — brief wait before next model
                logger.warning("Rate limited on %s, waiting 2s before next model", model)
                time.sleep(2)
                continue

            # Other errors (invalid key, model unavailable) — try next
            logger.warning("Chatbot error on %s: %s", model, e)
            continue

    logger.error("All Gemini models failed. Last error: %s", last_error)
    return JsonResponse(
        {"reply": "I'm having trouble connecting right now. Please try again in a moment, or contact us directly."},
        status=200,
    )
