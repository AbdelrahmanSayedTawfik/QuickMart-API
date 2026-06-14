import re
from django.core.exceptions import ValidationError


class PasswordValidator:
    MIN_LENGTH = 8
    @classmethod
    def validate(cls, password: str) -> None:
        if len(password) < cls.MIN_LENGTH:
            raise ValidationError(f"Password must be at least {cls.MIN_LENGTH} characters long.")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one special character.")
        
    @classmethod
    def get_help_text(cls) -> str:
        return (
            f"Your password must contain at least {cls.MIN_LENGTH} characters, "
            "including at least one uppercase letter, one lowercase letter, "
            "one digit, and one special character."
        )    