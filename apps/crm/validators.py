"""CuraSuite — CRM Validators"""
from django.core.exceptions import ValidationError
import re


def validate_indian_phone(value: str) -> None:
    """Validate Indian mobile or landline number (loose check)."""
    cleaned = re.sub(r"[\s\-\(\)\+]", "", value)
    if cleaned and not re.match(r"^[6-9]\d{9}$|^0\d{10}$|^\d{11,12}$", cleaned):
        raise ValidationError("Enter a valid Indian phone number.")


def validate_message_length(value: str) -> None:
    if len(value.strip()) < 10:
        raise ValidationError("Please provide at least 10 characters in your message.")
