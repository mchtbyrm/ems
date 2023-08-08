from django.core.validators import ValidationError
from django.utils.translation import gettext_lazy as _

from ems.constants import SPECIAL_CHARACTERS


class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _("This password must contain at least 8 characters."),
                code='password_too_short',
            )
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _("This password must contain at least 1 digit."),
                code='password_no_number',
            )
        if not any(char.isalpha() for char in password):
            raise ValidationError(
                _("This password must contain at least 1 letter."),
                code='password_no_letter',
            )
        if not any(char.isupper() for char in password):
            raise ValidationError(
                _("This password must contain at least 1 uppercase letter."),
                code='password_no_upper',
            )
        if not any(char.islower() for char in password):
            raise ValidationError(
                _("This password must contain at least 1 lowercase letter."),
                code='password_no_lower',
            )
        if not any(char in SPECIAL_CHARACTERS for char in password):
            raise ValidationError(
                _("This password must contain at least 1 special character."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Your password must contains at least 8 characters, "
            "1 digit, 1 letter, 1 uppercase letter, 1 lowercase letter and 1 special character."
        )
