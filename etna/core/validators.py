from django.core.exceptions import ValidationError


class PositiveIntegerStringValidator:
    """
    Validate that the input is a positive integer that falls within the specified
    `min` and `max` range, otherwise raise ValidationError.
    """

    def __init__(self, min: int = None, max: int = None, msg: str = None):
        self.min = min
        self.max = max
        if msg:
            invalid_message = msg
        else:
            invalid_message = "Enter a positive number"
            if min is not None and max is not None:
                invalid_message += f" between {min} and {max}."
            elif min:
                invalid_message += f" greater than or equal to {min}."
            elif max:
                invalid_message += f" less than or equal to {max}."
            else:
                invalid_message += "."
        self.messages = {"invalid": invalid_message}

    def __call__(self, value):
        if not value:
            return None
        if not value or not value.isdigit():
            raise ValidationError(
                self.messages["invalid"], code="invalid", params={"value": value}
            )
        intval = int(value)
        if self.min is not None and intval < self.min:
            raise ValidationError(
                self.messages["invalid"], code="invalid", params={"value": value}
            )
        if self.max is not None and intval > self.max:
            raise ValidationError(
                self.messages["invalid"], code="invalid", params={"value": value}
            )
