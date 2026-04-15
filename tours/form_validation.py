from django.core.exceptions import ValidationError

def validation_less_than_0(value):
    if value <= 0:
        raise ValidationError("Value must be a greater than 0.")
    return value
