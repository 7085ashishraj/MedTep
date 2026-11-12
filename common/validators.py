from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

phone_validator = RegexValidator(
    regex=r"\A\+?[0-9]{7,15}\Z",
    message="Enter 7 to 15 digits, optionally starting with +; omit spaces.",
)
latitude_validators = [
    MinValueValidator(Decimal("-90")),
    MaxValueValidator(Decimal("90")),
]
longitude_validators = [
    MinValueValidator(Decimal("-180")),
    MaxValueValidator(Decimal("180")),
]
