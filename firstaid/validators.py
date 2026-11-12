from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils import timezone


def validate_https_source(value):
    URLValidator(schemes=["https"])(value)
    parsed = urlsplit(value)
    if parsed.username or parsed.password:
        raise ValidationError("Source links must not contain login credentials.")


def validate_not_future(value):
    if value > timezone.localdate():
        raise ValidationError("A check or review date cannot be in the future.")
